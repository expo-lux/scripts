--cкрипт для копирования статусов и дат отправки фото из photo_send_error в photo
with last_attempts as (
    -- этот запрос возвращает только последние попытки отправки в serv, т.к. attempt=1
    -- данные берутся из photo_send_error
    select * from  (
        SELECT photo_id, attempt_timestamp,
               -- error_code - статус отправки в serv, 0 - успех, в остальных случаях 2 - неудача
               case
                   when error_code is null then 0
                   else 2
               end as error_code,
               -- attempt - номер попытки отправки в serv
               ROW_NUMBER() OVER (
                   PARTITION BY photo_id
                   ORDER BY
                       attempt_timestamp DESC
                   ) as attempt
        from photo_send_error
        ) as subquery
    where attempt = 1
)
-- взять данные из last_attempt и обновить ими таблицу photo
update photo
set dit_sending_status = last_attempts.error_code,
    dit_sent_timestamp = last_attempts.attempt_timestamp
from last_attempts
where last_attempts.photo_id = photo.id;