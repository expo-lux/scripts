#### Описание

Скрипт для отправки данных из таблицы photo БД МП на сервер serv.
Настройки считываются из `config.json`, интервал запрашиваемых данных из БД 
берется из переменных окружения `S_FROM`, `S_TO`.
` "dry_run": true` - запуск без отправки на сервер serv. 

#### Сборка

```shell script
TAG=photo:0.5
docker build -t "${TAG}" .
```

#### Развертывание
Доставить образ на сервер

Выставить нужное значение `dry_run` в `config.json`

Скопировать `photo.sh`, `config.json` в `/opt/reporting/` 

Отправка по cron - выполнить команду `crontab -e`, добавить строку
```shell script
PATH=/usr/local/bin:/usr/bin:/bin:/usr/games
* * * * * /opt/reporting/photo.sh
```
Проверить название образа и пути к файлам в `/opt/reporting/photo.sh`

#### Отправка данных вручную
Отправить данные за `2020-04-28 21:15:01 .. 2020-04-28 21:30:01` с помощью образа `contact:0.5` 
```shell script
export LOGPATH=/opt/reporting/logs/photo/processing.log
export CONFPATH=/opt/reporting/photo_config.json
docker run --rm -d -e S_FROM=`date -d "2020-04-28T21:15:01" --iso=seconds` -e S_TO=`date -d "2020-04-28T21:30:01" --iso=seconds` -v "${CONFPATH}":/app/config.json -v "${LOGPATH}":/app/processing.log photo:0.5
```
  
