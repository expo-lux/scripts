#!/bin/sh
LOGPATH=/opt/reporting/logs/photoraw/processing.log
DATAPATH=/opt/photos/raw_logs
/usr/bin/docker run --rm --cpus="1" --memory=512m --network=host -d \
           -e db=divmob \
           -e dbhost=div-postgres.focus.local \
           -e dbport=5433 \
           -e dbuser=divmob \
           -e dbpasswd=pass \
           -e endpoint=https://test.focus.ru/photo/ \
           -e user=apiuser \
           -e passwd=apipass \
           -v "${LOGPATH}":/app/processing.log \
           -v "${DATAPATH}":/app/data/ \
           photoraw:0.2