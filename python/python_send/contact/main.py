import json
import os
import requests, argparse
import sys
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.extras import RealDictCursor
from psycopg2 import Error
import logging
import traceback
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


# функция переноса контактов из БД PostgreSqL на удаленный сервер, принимающий post-запросы
# данные для подключения к базе и url сервера считываются из config.json
# границы временного интервала берутся из окружения:
# s_to - верхняя граница
# если dry_run=True - post запрос не выполняется
# из data берется event_occurred или upload_date -что первым будет не null
# из результата запроса исключаются записи с тестовых девайсов

def Transfer(db, user, passwd, host, port, remote_serv, dry_run=True):
    obj = {}
    try:
        ssn = requests.Session()
        # пытаемся отослать данные серверу за 2 попытки
        retries = Retry(total=2,
                        backoff_factor=1)
        ssn.mount(remote_serv, HTTPAdapter(max_retries=retries))

        s_to = os.environ["S_TO"]
        logger.debug("Connect to database")
        conn = psycopg2.connect(dbname=db, user=user, password=passwd, host=host, port=port)
        conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        logcursor = conn.cursor(cursor_factory=RealDictCursor)

        logger.debug("Run PostgreSql query")
        logger.debug("Search data not uploaded or uploaded with error, upload_date up to " + s_to)
        cursor.execute("select id, secondname, firstname, middlename, birthdate, doc_seria_number, phone, "
                       "scenario_id, prescript_number, "
                       "prescript_quarantine_address_fias_code, prescript_quarantine_address, prescript_quarantine_address_apt, "
                       "prescript_quarantine_enddate, "
                       "epidemic_case_id, role, "
                       "latitude, longitude, "
                       "to_char(upload_date, 'YYYY-MM-DD\"T\"HH24:MI:SS.MS') as upload_date, "
                       "agreement_quarantine_address_fias_code, agreement_quarantine_address, agreement_quarantine_address_apt, "
                       "agreement_quarantine_date, "
                       "event_address_fias_code, event_address, event_address_apt, "
                       "to_char(least(coalesce(event_occurred, upload_date),upload_date), 'YYYY-MM-DD\"T\"HH24:MI:SS.MS') as event_occurred "
                       "from data "
                       "where upload_date < %s and "
                       "(sit_sending_status is null or sit_sending_status in (1,2)) and status=2 "
                       "and enable_send_sit is True  "
                       "order by upload_date "
                       "limit 1000", (s_to,))
        for row in cursor:
            arr = []
            obj = row.copy()
            obj['latitude'] = str(row['latitude'])
            obj['longitude'] = str(row['longitude'])
            obj['organization'] = None
            obj['sick_state'] = None
            obj['sick_action'] = None
            obj['sick_severity'] = None
            obj['hospital_name'] = None
            obj['observator_name'] = None
            obj['event_succeeded'] = None
            obj['event_failure_reason'] = None
            obj['event_failure_comment'] = None
            obj['sick_action_status'] = None
            obj['device_id'] = None
            obj['discharge_date'] = None
            obj['discharge_reason'] = None
            obj['discharge_comment'] = None
            obj['hospital_guid'] = None
            obj['observator_guid'] = None
            obj['organization_guid'] = None
            obj['epidemic_case_guid'] = None
            obj['risk_group'] = None

            if (row['prescript_quarantine_address_fias_code']):
                if (row['prescript_quarantine_address']):
                    obj['prescript_quarantine_address'] = obj['prescript_quarantine_address'] + ' кв. ' + obj[
                        'prescript_quarantine_address_apt']

            if (row['agreement_quarantine_address_fias_code']):
                if (row['agreement_quarantine_address']):
                    obj['agreement_quarantine_address'] = obj['agreement_quarantine_address'] + ' кв. ' + obj[
                        'agreement_quarantine_address_apt']

            if (row['event_address_fias_code']):
                if (row['event_address']):
                    obj['event_address'] = obj['event_address'] + ' кв. ' + obj['event_address_apt']

            if (row['birthdate']):
                obj['birthdate'] = str(row['birthdate'])
            if (row['agreement_quarantine_date']):
                obj['agreement_quarantine_date'] = str(row['agreement_quarantine_date'])
            if (row['prescript_quarantine_enddate']):
                obj['prescript_quarantine_enddate'] = str(row['prescript_quarantine_enddate'])

            arr.append(obj)
            # js_str = json.dumps(arr)
            log_string = obj['id']
            if not dry_run:
                logger.debug("POST data")
                dest_code = 1  # DIT
                data_now = datetime.now()
                data_id = obj['id']
                error_code = None
                stack_trace = None
                error_message = None
                response = None
                # sit_sending_status:
                # NULL - запись не отправлялась,
                # 0 - успешно доставлена, 2 - ошибка отправки из-за недоступности сервиса
                sit_sending_status = None
                try:
                    # постим данные используя сессию и повторы
                    response = ssn.post(remote_serv, json=arr)
                    # если статус ответа 4xx 5xx, возбуждаем исключение типа HTTPError, которое далее перехватываем
                    response.raise_for_status()
                    log_string += ',' + str(response.status_code)
                    sit_sending_status = 0
                except Exception as e:
                    error_message = type(e).__name__
                    stack_trace = traceback.format_exc()
                    # если сервис вернул код ошибки 4xx 5xx => записываем его в error_code,
                    # если исключение возникло по другой причине (таймаут, сеть)
                    # то записываем 1
                    if response is None:
                        error_code = 1
                    else:
                        error_code = response.status_code
                    sit_sending_status = 2
                    log_string += ',' + str(error_code)
                    logger.error(stack_trace)
                    try:
                        # только в случае ошибок
                        # логируем в таблицу data_send_error результат post'а
                        logger.debug("Insert into data_send_error")
                        data_error_query = "insert into " \
                                           "data_send_error(destination, data_id, attempt_timestamp, error_code, error_message, stack_trace) " \
                                           "values(%s, %s, %s, %s, %s, %s);"
                        logcursor.execute(data_error_query,
                                          (dest_code, data_id, data_now, error_code, error_message, stack_trace))
                        logger.debug(str(logcursor.rowcount) + " rows affected")
                    except Exception as ex:
                        logger.error(traceback.format_exc())

                log_string += ',' + obj['upload_date'] + ',' + obj['event_occurred']
                logger.debug(log_string)

                update_sit_status_query = "update data " \
                                          "set sit_sending_status=%s, sit_sent_timestamp=%s, " \
                                          "sit_data_send_error_error_code=%s, " \
                                          "sit_data_send_error_error_message=%s, " \
                                          "sit_data_send_error_stack_trace=%s " \
                                          "where id=%s;"
                try:
                    logcursor.execute(update_sit_status_query,
                                      (sit_sending_status, data_now, error_code, error_message, stack_trace, data_id))
                    logger.debug("Update status in data: " + str(logcursor.rowcount) + " rows affected")
                except Exception:
                    logger.error(traceback.format_exc())

            else:
                logger.debug("dry_run - nothing to do")
                log_string += ',not_applicable'
                logger.debug(log_string)


    except Exception as ex:
        logger.error(traceback.format_exc())
        sys.exit(1)
    finally:
        if (conn):
            cursor.close()
            logcursor.close()
            conn.close()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename='processing.log')

    logger = logging.getLogger('ContactTransfer')
    logger.setLevel(logging.DEBUG)
    # отключаем сообщения в общий лог о повторной посылке (retries)  от urllib3
    logging.getLogger('requests').setLevel(logging.CRITICAL)
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)

    try:
        file = open("config.json", 'r', encoding='utf-8')
        conf = json.load(file)
    except Exception as e:
        logger.error(traceback.format_exc())
        sys.exit(2)
    finally:
        file.close()

    Transfer(conf['dbname'], conf['user'], conf['password'], conf['host'], conf['port'],
             conf['remote_server'], conf['dry_run'])