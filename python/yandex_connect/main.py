from bottle import route, run, request
import http.client
import urllib.parse
import json

# Идентификатор приложения
client_id = 'c461b2f65'
# Пароль приложения
client_secret = '2429004addac66eea2a'

import os
import csv
import sys
import requests

TOKEN = os.environ.get('TOKEN')
USER_AGENT = 'Directory Sync Example'


@route('/')
def index():
    # Если скрипт был вызван с указанием параметра "code" в URL,
    # то выполняется запрос на получение токена
    if request.query.get('code'):
        # Формирование параметров (тела) POST-запроса с указанием кода подтверждения
        query = {
            'grant_type': 'authorization_code',
            'code': request.query.get('code'),
            'client_id': client_id,
            'client_secret': client_secret,
        }
        query = urllib.parse.urlencode(query)

        # Формирование заголовков POST-запроса
        header = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Выполнение POST-запроса и вывод результата
        connection = http.client.HTTPSConnection('oauth.yandex.ru')
        connection.request('POST', '/token', query, header)
        response = connection.getresponse()
        result = response.read()
        connection.close()

        # Токен необходимо сохранить для использования в запросах к API Директа
        return json.loads(result)['access_token']


def get_organizations():
    """Забирает из Директории данные об уже существующих отделах
    и возвращает словарь {'Название отдела': department_id}
    """
    params = {
        'fields': 'name',
    }
    headers = {
        'Authorization': 'OAuth ' + TOKEN,
        'User-Agent': USER_AGENT,
        'Accept': 'application/json'
    }
    # В целях простоты примера мы игнорируем тот факт, что
    # отделов может быть больше 20 и они не поместятся в
    # один запрос. В реальном коде тут надо будет анализировать
    # ключ links и делать дополнительные запросы.
    response = requests.get(
        'https://api.directory.yandex.net/v6/organizations/',
        params=params,
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
    response_data = response.json()
    results = response_data['result']
    results = {
        organization['name']: organization['id']
        for organization in results
    }
    return results


def get_groups(org_id):
    params = {
        'fields': 'email,name,label,type,created',
    }
    headers = {
        'Authorization': 'OAuth ' + TOKEN,
        'User-Agent': USER_AGENT,
        #'X-Org-ID': org_id,
        'X-Org-ID': '11',
        'Accept': 'application/json'
    }
    response = requests.get(
        'https://api.directory.yandex.net/v6/groups/',
        params=params,
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
    response_data = response.json()
    results = response_data['result']
    res = {}
    for group in results:
        if group['email']:
            res[group['email']] = group['id']
        else:
            res[group['name']] = group['id']

    # results = {
    #     group['email']: group['id'] if x is not None else '' for group in results
    # }
    return res


def get_departments(org_id):
    """Забирает из Директории данные об уже существующих отделах
    и возвращает словарь {'Название отдела': department_id}
    """
    params = {
        'fields': 'name',
    }
    headers = {
        'Authorization': 'OAuth ' + TOKEN,
        'User-Agent': USER_AGENT,
        'X-Org-ID': org_id
    }
    # В целях простоты примера мы игнорируем тот факт, что
    # отделов может быть больше 20 и они не поместятся в
    # один запрос. В реальном коде тут надо будет анализировать
    # ключ links и делать дополнительные запросы.
    response = requests.get(
        'https://api.directory.yandex.net/v6/departments/',
        params=params,
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
    response_data = response.json()
    results = response_data['result']
    results = {
        department['name']: department['id']
        for department in results
    }
    return results


def get_enabled_users_from_group(org_id, grp_id):
    params = {
        'fields': 'email,is_enabled',
        'group_id': grp_id,
        #'group_id': 11,
        'per_page': '1000',
    }
    headers = {
        'Authorization': 'OAuth ' + TOKEN,
        'User-Agent': USER_AGENT,
        'X-Org-ID': org_id
    }
    # В целях простоты примера мы игнорируем тот факт, что
    # сотрудников может быть больше 20 и они не поместятся в
    # один запрос. В реальном коде тут надо будет анализировать
    # ключ links и делать дополнительные запросы.
    response = requests.get(
        'https://api.directory.yandex.net/v6/users/',
        params=params,
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
    response_data = response.json()
    results = response_data['result']
    return {user['email'] for user in results if user['is_enabled']}


def get_enabled_users_from_dep(org_id, dep_id):
    """Забирает из Директории данные об уже существующих сотрудниках.
    и возвращает set из из логинов.
    """
    params = {
        'fields': 'email,is_enabled',
        'department_id': dep_id,
        'per_page': '1000'
        # ,
        # 'is_enabled': False
        # ,
        # 'id' : '22'
    }
    headers = {
        'Authorization': 'OAuth ' + TOKEN,
        'User-Agent': USER_AGENT,
        'X-Org-ID': org_id
        # 'X-Org-ID': '11'
    }
    # В целях простоты примера мы игнорируем тот факт, что
    # сотрудников может быть больше 20 и они не поместятся в
    # один запрос. В реальном коде тут надо будет анализировать
    # ключ links и делать дополнительные запросы.
    response = requests.get(
        'https://api.directory.yandex.net/v6/users/',
        params=params,
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
    response_data = response.json()
    results = response_data['result']
    return {user['email'] for user in results if user['is_enabled']}


def main():
    org = get_organizations()
    #org = { "x.com" : "11" }
    for org_name, org_id in org.items():
        print("-" * 30)
        print("Организация: " + org_name)
        print("Отделы:")
        dep = get_departments(str(org_id))
        for dep_name, dep_id in dep.items():
            usr = get_enabled_users_from_dep(str(org_id), str(dep_id))
            if usr:
                print("\t" + dep_name + ":")
                for user in usr:
                    print("\t\t" + user)
        print("Команды(рассылки):")
        grp = get_groups(str(org_id))
        for grp_name, grp_id in grp.items():
            usr = get_enabled_users_from_group(str(org_id), str(grp_id))
            if usr:
                print("\t" + grp_name + ":")
                for user in usr:
                    print("\t\t" + user)


main()

# Запускаем веб-сервер
# run(host='0.0.0.0', port=8199, quiet=False)
