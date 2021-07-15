#!/bin/sh
LOGPATH=/opt/reporting/logs/contact/processing.log
CONFPATH=/opt/reporting/contact_config.json
DATE_TO=`date -d "-5 minutes" +"%Y-%m-%dT%H:%M"`:00
/usr/bin/docker run --rm -d --cpus="1" --memory=512m --network=host -e S_TO=${DATE_TO} -v "${CONFPATH}":/app/config.json -v "${LOGPATH}":/app/processing.log contact:2.1