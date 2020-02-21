#!/bin/bash
COMMAND=$1

if [ -z "$COMMAND" ]
then
   echo "Options..."
   echo "   restart - restart twilio.webhook.service"
   echo "   start   - start twilio.webhook.service"
   echo "   stop    - stop twilio.webhook.service"
   echo "   status  - get status of twilio.webhook.service"
   echo "   enable  - enable twilio.webhook.service at bootup"
   echo "   disable - disable twilio.webhook.service at bootup"
   sudo ps aux | grep twilio 
else
   sudo systemctl $COMMAND twilio.webhook.service
   sudo ps aux | grep twilio
fi

if [ "$COMMAND" = "start" ] || [ "$COMMAND" = "restart" ]
then
   echo "reloading..."
   sudo systemctl daemon-reload
fi

