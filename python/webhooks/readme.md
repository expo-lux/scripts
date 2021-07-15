Склонировать репозиторий:  
```
git clone http://i.ivanov@192.168.222.3:8080/scm/git/scm-manager-webhooks
```
Образец настроек лежит в config.yml
#### Как проверить работу
Запустить скрипт в контейнере:
```
docker-compose up
```
Отредактировать тестовый json (заменить строку "mail": "i.ivanov@gmail.com" своим почтовым ящиком)
```
vim ./tests/test_email_substitution_request.json
```
Проверить работу скрипта отправив тестовый POST запрос:
```
curl -d @.\tests\test_email_substitution_request.json -X POST http://localhost:4001
```
Письмо должно прийти в почтовый ящик указанный в тестовом json
