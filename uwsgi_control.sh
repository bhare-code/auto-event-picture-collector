#!/bin/bash
COMMAND=$1

if [ -z "$COMMAND" ]
then
   echo "Options..."
   echo "   restart - restart emperor.uwsgi.service"
   echo "   start   - start emperor.uwsgi.service"
   echo "   stop    - stop emperor.uwsgi.service"
   echo "   status  - get status of emperor.uwsgi.service"
   echo "   enable  - enable emperor.uwsgi.service at bootup"
   echo "   disable - disable emperor.uwsgi.service at bootup"
   sudo ps aux | grep uwsgi 
else
   sudo systemctl $COMMAND emperor.uwsgi.service
   sudo ps aux | grep uwsgi
fi

if [ "$COMMAND" = "start" ] || [ "$COMMAND" = "restart" ]
then
   echo "reloading..."
   sudo systemctl daemon-reload
fi

