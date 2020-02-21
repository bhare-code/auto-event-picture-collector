#!/bin/bash
COMMAND=$1

if [ -z "$COMMAND" ]
then
   echo "Options..."
   echo "   restart - restart slideshow.service"
   echo "   start   - start slideshow.service"
   echo "   stop    - stop slideshow.service"
   echo "   status  - get status of slideshow.service"
   echo "   enable  - enable slideshow.service at bootup"
   echo "   disable - disable slideshow.service at bootup"
   sudo ps aux | grep slideshow
else
   sudo systemctl $COMMAND slideshow.service
   sudo ps aux | grep slideshow
fi

if [ "$COMMAND" = "start" ] || [ "$COMMAND" = "restart" ]
then
   echo "reloading..."
   sudo systemctl daemon-reload
fi

