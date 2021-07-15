import json
import os
import requests, argparse
import sys
import base64
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import DictCursor
from psycopg2 import Error
import logging
import traceback
from hurry.filesize import size
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from pathlib import Path

def SearchInFolders(data_folders: list, id: str):
    """
    поиск фото с идентификатором id в списке папок data_folders
    :param data_folders: список папок
    :param id: id фотографии
    :return: если фото найдено, возвращается полный путь к нему, если нет - пустая строка
    """
    res = ""
    for folder in data_folders:
        path = Path(folder) / id[0:2] / id[2:4] / id # make crossplatform path
        if path.is_file():
            res = path
            break
        else:
            continue
    return res

def UpdatePhotoDIT(cursor, dit_sending_status, photo_id):
    """
    Запись результатов пересылки в таблицу photo
    :param cursor: курсор к СУБД
    :param dit_sending_status: результат пересылки
    :param photo_id: id фотографии
    :return:
    """
    data_now = datetime.now()
    update_dit_status_query = "update photo " \
                              "set dit_sending_status=%s, dit_sent_timestamp=%s " \
                              "where id=%s;"
    try:
        cursor.execute(update_dit_status_query, (dit_sending_status, data_now, photo_id))
        logger.debug("Update status in photo: " + str(cursor.rowcount) + " rows affected")
    except Exception as e3:
        logger.error(traceback.format_exc())

def LogBusinessError(cursor, photo_id):
    """
    логирование бизнес-ошибки в БД
    """
    logger.debug(photo_id + " business error")
    dit_sending_status = 1
    UpdatePhotoDIT(cursor, dit_sending_status, photo_id)

def LogSuccess(cursor, photo_id):
    logger.debug(photo_id + " success")
    dit_sending_status = 0
    UpdatePhotoDIT(cursor, dit_sending_status, photo_id)

def LogServiceUnreachable(cursor, photo_id):
    logger.debug(photo_id + " service unreachable error")
    dit_sending_status = 2
    UpdatePhotoDIT(cursor, dit_sending_status, photo_id)

def LogInPhotoSendError(cursor, photo_id, error_code, error_message, stack_trace):
    dest_code = 1  # DIT
    try:
        data_now = datetime.now()
        # только в случае ошибок отправки
        # логируем в таблицу photo_send_error результат post'а
        logger.debug("Insert into photo_send_error")
        photo_event_query = "insert into " \
                            "photo_send_error(destination, photo_id, attempt_timestamp, error_code, error_message, stack_trace) " \
                            "values(%s, %s, %s, %s, %s, %s);"
        cursor.execute(photo_event_query,
                          (dest_code, photo_id, data_now, error_code, error_message, stack_trace))
        logger.debug(str(cursor.rowcount) + " rows affected")
    except Exception as e2:
        logger.error(traceback.format_exc())


#функция переноса изображений из БД PostgreSqL на удаленный сервер, принимающий post-запросы
#данные для подключения к базе и url сервера считываются из config.json
#границы временного интервала берутся из окружения:
#s_to - верхняя граница
#если dry_run=True - post запрос не выполняется
# передаются следующие поля из таблицы photo: id data_id photo_type device_id upload_date photo(в base64)
# из data берется event_occurred или upload_date -что первым будет не null

def Transfer(db, user, passwd, host, port, remote_serv, s_data_folders, dry_run=True):
    obj = {}
    conn = None
    try:
        ssn = requests.Session()
        # пытаемся отослать данные серверу за 2 попытки
        retries = Retry(total=2,
                        backoff_factor=1)
        ssn.mount(remote_serv, HTTPAdapter(max_retries=retries))

        #s_from = os.environ["S_FROM"]
        s_to = os.environ["S_TO"]
        logger.debug("Connect to database")
        conn = psycopg2.connect(dbname=db, user=user, password=passwd, host=host, port=port)
        conn.autocommit = True
        cursor = conn.cursor(cursor_factory=DictCursor)
        logcursor = conn.cursor(cursor_factory=DictCursor)

        logger.debug("Run PostgreSql query")
        logger.debug("Search data with upload_date up to " + s_to)

        cursor.execute("select p.id, data_id, photo_type, photo, p.device_id, to_char(p.upload_date, 'YYYY-MM-DD\"T\"HH24:MI:SS.MS') as upload_date," \
                       "to_char(least(coalesce(d.event_occurred, d.upload_date), d.upload_date), 'YYYY-MM-DD\"T\"HH24:MI:SS.MS') as event_occurred " \
                       "from photo p " \
                       "inner join data d on p.data_id = d.id " \
                       "where d.registry_sending_status = 0 and (p.dit_sending_status is null or p.dit_sending_status = 2) "
                       "and d.enable_send_dit = True "
                       "order by upload_date asc "
                       "limit 100 ")
        l = ''
        data_folders = s_data_folders.split(",")
        photo64 = None
        for row in cursor:
            obj['id'] = row['id']
            id = obj['id']
            logger.debug("Encode " + id + " with base64")
            if row['photo'] is None:
                # если фото лежит на диске
                filepath = SearchInFolders(data_folders, id)
                if filepath:
                    try:
                        raw = open(filepath, 'rb')
                        content = raw.read()
                        photo64 = base64.encodebytes(content)
                    except Exception:
                        logger.error(traceback.format_exc())
                        LogBusinessError(logcursor, id)
                        continue
                    else:
                        if raw:
                            raw.close()
                else:
                    logger.error(id + " can't find file in " + s_data_folders)
                    LogBusinessError(logcursor, id)
                    continue
            else:
                # если фото лежит в БД
                photo64 = base64.encodebytes(row['photo'].tobytes())
            obj['data_id'] = row['data_id']
            obj['photo_type'] = row['photo_type']
            obj['device_id'] = row['device_id']
            obj['upload_date'] = row['upload_date']
            obj['photo'] = photo64.decode('ascii')
            l = size(len(obj['photo']))
            obj['event_occurred'] = row['event_occurred']

            if not dry_run:

                photo_id = obj['id']
                logger.debug("POST " + photo_id)
                error_code = None
                stack_trace = None
                error_message = None
                response = None
                try:
                    response = ssn.post(remote_serv, json=obj)
                    response.raise_for_status() # в случае ошибки переходим в блок except
                    LogSuccess(logcursor, photo_id)
                    log_string = obj['id'] + ',' + str(response.status_code) + ',' + obj['upload_date'] + ',' + obj['event_occurred']
                    logger.debug(log_string)
                except Exception as e1:
                    error_message = type(e1).__name__
                    stack_trace = traceback.format_exc()
                    logger.error(stack_trace)
                    # если сервис вернул код ошибки 4xx 5xx => записываем его в error_code,
                    # если исключение возникло по другой причине (таймаут, сеть)
                    # то записываем 1
                    if response is None:
                        error_code = 1
                    else:
                        error_code = response.status_code
                    LogServiceUnreachable(logcursor, photo_id)
                    LogInPhotoSendError(logcursor, photo_id, error_code, error_message, stack_trace)
                    log_string = obj['id'] + ',' + str(error_code) + ',' + obj['upload_date'] + ',' + obj[
                        'event_occurred']
                    logger.debug(log_string)
            else:
                logger.debug("dry_run - nothing to do")
                logger.debug(obj['id'] + ',not_applicable')

    except Exception as e:
        logger.error(traceback.format_exc())
        sys.exit(1)
    finally:
        if conn:
            cursor.close()
            logcursor.close()
            conn.close()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename='processing.log')

    logger = logging.getLogger('PhotoTransfer')
    logger.setLevel(logging.DEBUG)
    # отключаем сообщения в общий лог о повторной посылке (retries)  от urllib3
    logging.getLogger('requests').setLevel(logging.CRITICAL)
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)

    try:
        file = open("/app/config.json", 'r', encoding='utf-8')
        conf = json.load(file)
    except Exception as e:
        logger.error(traceback.format_exc())
        sys.exit(2)
    else:
        file.close()

    Transfer(conf['dbname'], conf['user'], conf['password'], conf['host'], conf['port'],
             conf['remote_server'], conf['data_folders'], conf['dry_run'])
