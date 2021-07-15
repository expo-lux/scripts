import os
from os import listdir
from os.path import isfile, join
import json
import logging, traceback
import sys
import base64
# import dateutil.parser
import psycopg2
from psycopg2.extras import DictCursor
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.auth import HTTPBasicAuth
import datetime


def RawFilesModifiedInLastDay():
    """
    Функция возвращает список файлов
    В список добавляются только файлы, которые
    - лежат в <директория_скрипта>/data
    - имя файла начинается с  raw_photo_div-reestr-mobile-backend, заканчивается на raw_log
    - время изменения файла отстоит от текущего момента времени не более чем на 24ч.
    """
    rtn = []
    dir = Path(os.path.dirname(os.path.realpath(__file__))) / "data"  # make crossplatform path
    onlyfiles = [f for f in listdir(dir) if isfile(join(dir, f))]
    for f in onlyfiles:
        if f.startswith("raw_photo_div-reestr-mobile-backend") and f.endswith("raw_log"):
            path = dir / f
            filetimestamp = os.path.getmtime(path)
            cnv_time = datetime.datetime.fromtimestamp(filetimestamp)
            cur_time = datetime.datetime.now()
            hours = (cur_time - cnv_time).total_seconds() / 3600
            # обрабатываем только файлы измененные за последние 24 часа
            if hours < 24:
                rtn.append(path)
    return rtn

def ParseLine(line: str):
    """
    Парсит строку
    """
    str_date = line[:29]
    str_message = line[30:]
    unescaped = str_message.encode('utf-8').decode('unicode_escape')[1:-2]

    s = json.loads(unescaped)
    error = s["errorMessage"]
    value = json.loads(s["value"])

    obj = {}
    obj["id"] = value["id"]
    obj["contactId"] = value["contactId"]
    obj["deviceId"] = value["deviceId"].split('|')[0]  # исходная строка в виде 'device_id|version'
    obj["base64"] = value["base64"]
    obj["photoType"] = value["photoType"]
    obj["uploadDate"] = str_date
    return obj

def ExistsInDB(cursor, obj:dict):
    """
    Проверяет наличие записи с заданным id и photo_type в БД
    """
    logger.info(obj["id"] + " check in DB  with photo.type " + obj["photoType"])
    photo_query = "select count(id) from photo " \
                  "where id=%s and photo_type=%s"
    cursor.execute(photo_query, (obj["id"], int(obj["photoType"])))
    return bool(cursor.fetchone()[0])

def IsEmptyPhoto(obj:dict):
    """
    возвращает true если отсутствует фото (поле base64 - пустое)
    """
    return not bool(obj["base64"])

def PostPhoto(user, passwd, endpoint, photoobj):
    """"
    Post-Запрос в endpoint
    """
    ssn = requests.Session()
    # пытаемся отослать данные серверу за 2 попытки
    retries = Retry(total=2, backoff_factor=1)
    ssn.mount(endpoint, HTTPAdapter(max_retries=retries))
    try:
        # постим данные используя сессию и повторы
        logger.info(photoobj["id"] + " trying to post")
        response = ssn.post(endpoint, json=photoobj, auth=HTTPBasicAuth(user, passwd))
        # если статус ответа 4xx 5xx, возбуждаем исключение типа HTTPError, которое     далее перехватываем
        response.raise_for_status()
        # cursor.execute(photo_query, (id, data_id, photo_type, photo, device_id, upload_date))
        logger.info(photoobj["id"] + " success")
    except:
        logger.error(traceback.format_exc())


def ProcessFiles(user, passwd, endpoint, cursor):
    """
    Обработка файлов и публикация фото через API
    :param user: имя пользователя к API
    :param passwd: пароль к API
    :param endpoint: полный путь к /photo/ API
    :param cursor: курсор к БД для проверки наличия фото в БД
    """

    files = RawFilesModifiedInLastDay()

    for item in files:
        file = None
        try:
            file = open(item, 'r')
            logger.info("Parse " + file.name)
            contents = list(file)
            for line in contents:
                obj = ParseLine(line)

                if IsEmptyPhoto(obj):
                    continue

                # если таких записей нет, используем API для добавления
                if not ExistsInDB(cursor, obj):
                    PostPhoto(user, passwd, endpoint, obj)
                else:
                    logger.info(obj["id"] + " already in DB")
        except Exception as e:
            logger.error(traceback.format_exc())
        finally:
            if file:
                file.close()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename='processing.log')

    logger = logging.getLogger('photo_parse')
    logger.setLevel(logging.DEBUG)
    # отключаем сообщения в общий лог о повторной посылке (retries)  от urllib3
    logging.getLogger('requests').setLevel(logging.CRITICAL)
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)
    conn = None

    try:
        # СУБД и учетные данные для подключения к ней
        db = os.environ["db"]
        dbhost = os.environ["dbhost"]
        dbport = os.environ["dbport"]
        dbuser = os.environ["dbuser"]
        dbpasswd = os.environ["dbpasswd"]
        # эндпоинт и учетные данные для подключения к нему
        endpoint = os.environ["endpoint"]
        user = os.environ["user"]
        passwd = os.environ["passwd"]

        conn = psycopg2.connect(dbname=db, user=dbuser, password=dbpasswd, host=dbhost, port=dbport)
        conn.autocommit = True
        cursor = conn.cursor(cursor_factory=DictCursor)

        ProcessFiles(user, passwd, endpoint, cursor)

    except Exception as e:
        logger.error(traceback.format_exc())
        sys.exit(1)
    finally:
        if conn:
            cursor.close()
            conn.close()
