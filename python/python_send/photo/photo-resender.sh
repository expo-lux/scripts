#!/bin/sh
LOGPATH=/opt/reporting/logs/photo-resender/processing.log
CONFPATH=/opt/reporting/photo_config.json
DATE_TO=`date -d "-1 minutes" +"%Y-%m-%dT%H:%M"`:00
/usr/bin/docker run --rm  --cpus="1" --memory=512m -d -e S_TO=${DATE_TO} -v "${CONFPATH}":/app/config.json -v "${LOGPATH}":/app/processing.log -v /opt/photos/photos:/data -v /opt/photos2/photos:/data2 -v /opt/photos3/photos:/data3 photo-resender:0.1