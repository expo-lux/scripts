#### Описание

Скрипт парсит raw-логи из директории /app/data (учитываются только файлы изменившиеся за последние сутки) и пытается отправить их post-запросом на endpoint.

Лог записывается в /app/processing.log, все настройки берутся из переменных окружения. 

Настройки:

* db - название БД для проверки, не отправлялся ли уже данный photo id
* dbhost, dbport - сервер и порт СУБД
* dbuser, dbpasswd - учетка к БД
* endpoint, user, passwd - endpoint и учетка к нему

#### Сборка

```shell script
TAG=photoraw:0.2
docker build -t "${TAG}" .
```

#### Развертывание
Доставить образ на сервер

Выставить нужное значение переменных окружения в `photoraw.sh`

Скопировать `photoraw.sh` в `/opt/reporting/`

Настроить отправку по расписанию - в 3:05 каждый день
Для этого выполнить команду `crontab -e`, добавить строку
```shell script
PATH=/usr/local/bin:/usr/bin:/bin:/usr/games
5 3 * * * /opt/reporting/photoraw.sh
```