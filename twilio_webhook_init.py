import subprocess
from time import sleep


if __name__ == "__main__":
    sleep(15)
    subprocess.call('/home/pi/.nvm/versions/node/v12.16.0/bin/node /home/pi/.nvm/versions/node/v12.16.0/bin/twilio phone-numbers:update $TWILIO_PHONE_NUMBER --sms-url=http://localhost:80/sms', shell=True)
