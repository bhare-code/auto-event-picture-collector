# auto-event-picture-collector
Receive MMS messages using a Twilio number by running a full stack web server on a Raspberry Pi then retrieve all pictures attached and display them on a connected TV.

Minimum required Python version: 3.8.0 (although earlier versions starting from 3.6 ***should*** work, but have not been tested)
# Installation and Setup
## Raspberry Pi Image Setup
References:
- [Raspbian Full Desktop image](https://www.raspberrypi.org/downloads/raspbian/)
- [Etcher](https://www.balena.io/etcher/) - to flash microSD card
- [Win32 Disk Imager](https://sourceforge.net/projects/win32diskimager/) - alternative Windows-based tool used to flash microSD card
- [PuTTY](https://www.putty.org/) - Secure SHell (SSH) client tool used to access the Raspberry Pi
- [FileZilla](https://filezilla-project.org/) - secure FTP client used to transfer files to/from the Raspberry Pi

NOTE: The "Raspbian Buster with desktop and recommended software" image released on 2019-09-26 was used to create these instructions.  Other versions of Raspbian should work, but additional setup or configuration changes may be needed.

Download the latest version of Raspbian Desktop from RaspberryPi.org and flash onto a 16GB (or larger) micro SD card.  Etcher is recommended.  Win32 Disk Imager can also be used on Windows.
## Basic Raspbian Configuration
References:
- [Advanced IP Scanner] (https://www.advanced-ip-scanner.com/)

When booting the Raspberry Pi for the first time connect a keyboard, mouse and monitor before powering on the Raspberry Pi.

Tip: power on the monitor BEFORE powering on the Raspberry Pi.

Raspbian will boot into the Desktop.  Run the configuration as instructed to set your region, Wi-Fi credential, password, etc.  The software will also be updated automatically.

Tip: connect through Ethernet if at all possible.

Restart the Raspberry Pi when instructed after the upgrade.

To access the Raspberry Pi configuration tool click on the Raspberry Pi icon at the top-left of the screen and choose "Preferences" then "Raspberry Pi Configuration".
### Hostname (optional)
Under the "System" tab of the Raspberry Pi configuration tool modify the "Hostname" (e.g. EventServer) to make the system easier to identify on the network, especially if you have multiple Raspberry Pi's running on your network.
### SSH
Under the "Interfaces" tab enable SSH.
### VNC (optional)
Under the "Interfaces" tab enable VNC if you like to use VNC.

After all configuration changes are made reboot the Raspberry Pi.
## Upgrade Raspbian OS
Before continuing make sure that the OS is up-to-date by running the following commands via SSH or Terminal window when connected via VNC:

    $ sudo apt update && sudo apt dist-upgrade
    $ sudo apt autoremove
    $ sudo reboot now
## Install Needed Packages
    $ sudo apt update
    $ sudo apt install libncurses5-dev libncursesw5-dev libreadline6-dev libffi-dev
    $ sudo apt install libbz2-dev liblzma-dev libsqlite3-dev libgdbm-dev tk8.5-dev
    $ sudo apt install libjpeg8-dev
    $ sudo apt install python-imaging-tk
    $ sudo apt install python-virtualenv
## Upgrade Python3
This step is only necessary if the Raspberry Pi is not running the minimum required version of Python3.

Do the following to check the current version:

    $ python3 -V

If the current version of Python3 is earlier than the minimum required OR you would simply like to upgrade to a later version then do the following:

    $ sudo apt update
    $ cd ~
    $ mkdir python-source
    $ cd python-source/

Do the following to get the URL to the latest stable Python3 release:

* Navigate to [Python.org](https://www.python.org/)
* Hover over "Downloads" and select "Source code"
* Scroll down to find the latest stable Python 3.x release
* Copy the Gzipped source tarball link (e.g. right-click and select "Copy link address" if using the Chrome browser)

Download and unzip the source code into the "python-source" directory then compile Python.

NOTE: The following command assume that the Python version is 3.8.1.  Adjust the URL and version number on the commands as necessary.

    $ wget https://www.python.org/ftp/python/3.8.1/Python-3.8.1.tgz
    $ tar zxvf Python-3.8.1.tgz
    $ cd Python-3.8.1/
    $ ./configure --prefix=/usr/local/opt/python-3.8.1
    $ make
    $ sudo make install
    $ /usr/local/opt/python-3.8.1/bin/python3.8 --version

The response should be `Python 3.8.1` in this example.
## Configure Git
Do the following to configure Git on the Raspberry Pi:

    $ git config --global user.name “<your name>”
    $ git config --global user.email <your email>

Example:

    $ git config --global user.name “John Smith”
    $ git config --global user.email jsmith@notarealaddress.com

Use `git config --global --list` to validate the configuration.
## Setup Virtual Python Environment
Do the following to setup a virtual Python3 environment.  Modify the Python version number as necessary based on your actual installation.

    $ sudo mkdir /var/www
    $ sudo mkdir /var/www/sms
    $ cd /var/www/sms/
    $ sudo /usr/local/opt/python-3.8.1/bin/python3.8 -m venv .
## Setup Full Application Stack
References:
- [Tech Explorations<sup>TM</sup> Raspberry Pi Full Stack Raspbian](https://www.udemy.com/course/raspberry-pi-full-stack-raspbian/learn/lecture/9607938?start=15#overview)
- [Tech Explorations website](https://techexplorations.com/)
- [FutureShocked Raspberry Pi Full Stack Raspbian](https://github.com/futureshocked/RaspberryPiFullStack_Raspbian) - original full stack code on GitHub

Technically, most of this section is not absolutely necessary.  A simple Flask application is all that's needed.  But, if you want a robust, fully-functional web server running on the Raspberry Pi then follow the instructions below.

NOTE: the web stack related configuration files are based on the "Raspberry Pi Full Stack Raspbian" course from Tech Explorations<sup>TM</sup>.  I **highly** recommend this course if you would like to understand all of the components of a web application.  Dr. Peter Dalmaris takes you step-by-step through the process of setting up a Raspberry Pi and building a full stack web application to monitor sensor data.

Execute the following commands to install the needed web application stack components.  Notice that the virtutal environment created earlier is activated to ensure that all needed Python packages are installed into the Virtual Environment, not the system Python environment.

    $ cd /var/www/sms/
    $ . bin/activate
    (sms) $ sudo apt update
    (sms) $ sudo apt upgrade

NOTE: in many of the subsections below the first two commands from the list above are repeated.  This is not necessary.  They are included simply as a reminder that the commands are executed from within the virtual environment.
### Test NGiNX Web Server
Navigate to the IP address of the Raspberry Pi from another device on the same LAN.  The default NGiNX webpage should appear.  The text displayed will look similar to the following:

  ```
  Welcome to nginx!
  If you see this page, the nginx web server is successfully installed and working. Further configuration is required.

  For online documentation and support please refer to nginx.org.
  Commercial support is available at nginx.com.

  Thank you for using nginx.
  ```
## Install Flask
Run the following commands to install Flask into the virtual environment making sure that the version of pip in the virtual environment is up-to-date as well:

    $ cd /var/www/sms/
    $ . bin/activate
    (sms) $ sudo bin/pip install --upgrade pip
    (sms) $ sudo bin/pip install flask

## Install uWSGI
Run the following commands to install uWSGI into the virtual environment:

    $ cd /var/www/sms/
    $ . bin/activate
    (sms) $ sudo bin/pip install uwsgi

## Clone Source Code to Raspberry Pi
Do the following to clone the source code onto the Raspberry Pi:

    $ cd
    $ git clone https://github.com/bhare-code/auto-event-picture-collector.git

Enter your github credentials when prompted.
### Configure Web server
Do the following to configure the web server.  Note that the default configuration for NGiNX is deleted.

    $ cd /var/www/sms/
    $ . bin/activate
    (sms) $ cd /etc/nginx/sites-enabled/
    (sms) $ sudo rm default
    (sms) $ cd /var/www/sms/
    (sms) $ sudo cp ~/auto-event-picture-collector/sms_nginx.conf .
    (sms) $ sudo ln -s /var/www/sms/sms_nginx.conf /etc/nginx/conf.d/
    (sms) $ sudo cp ~/auto-event-picture-collector/sms_uwsgi.ini .
    (sms) $ sudo mkdir /var/log/uwsgi

### Test Web Server Configuration
Do the following to test the web server configuration.  The test_server_config.py file is a very simple stripped-down Flask application.

    $ cd /var/www/sms/
    $ . bin/activate
    (sms) $ sudo cp ~/auto-event-picture-collector/test_server_config.py sms.py
    (sms) $ sudo /etc/init.d/nginx restart
    (sms) $ sudo bin/uwsgi --ini /var/www/sms/sms_uwsgi.ini

Navigate to the IP address of the Raspberry Pi from another device on the same LAN.  The test webpage should appear.  The text displayed will be as follows:

```
Hello from my web server!
```
## Persist Web Server
Make the web server initialization persistent:

    (sms) $ sudo cp ~/auto-event-picture-collector/emperor.uwsgi.service /etc/systemd/system/
    (sms) $ sudo systemctl start emperor.uwsgi.service

Verify that the service is running:

    (sms) $ systemctl status emperor.uwsgi.service

Enable the service to run at bootup:

    (sms) $ sudo systemctl enable emperor.uwsgi.service

### Test Web Server Persistence
Reboot the Raspberry Pi using `sudo reboot now` then navigate to the IP address of the Raspberry Pi from another device on the same LAN.  The test webpage should appear like it did before.  The text displayed will be as follows:

```
Hello from my web server!
```
## Install and Setup Twilio
Do the following to install the Twilio Python package into the virtual environment:

    $ cd /var/www/sms/
    $ . bin/activate
    (sms) $ sudo bin/pip install twilio

### Install Twilio CLI
References:
- [Twilio Quickstart Pyton](https://www.twilio.com/docs/sms/quickstart/python)
- [NVM Installation and Update](https://github.com/nvm-sh/nvm#installation-and-update)
- [Nodejs Upgrade](https://thisdavej.com/upgrading-to-more-recent-versions-of-node-js-on-the-raspberry-pi/)

Do the following to install the Twilio CLI:

    $ cd
    $ sudo apt update
    $ curl -sL https://deb.nodesource.com/setup_13.x | sudo -E bash -
    $ sudo apt install -y nodejs
    $ node -v
    $ curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.1/install.sh | bash
    $ sudo apt autoremove
    $ sudo reboot now
    ...
    $ nvm install --lts
    $ nvm use <version reported from last command>
    Example: $ nvm use v12.16.0
    $ sudo apt install libsecret-1-dev
    $ sudo apt install gnome-keyring
    $ npm install twilio-cli -g
    $ npm install twilio-cli@latest -g

### Setup Twilio Account
References:
- [Twilio](https://www.twilio.com/)

Use the link above to access the Twilio website.  Create an account and request a free phone number that is capable of SMS and MMS.  You can always upgrade later if you want by purchasing the phone number.

### Add Environment Variables to .bashrc File
Do the following to setup all Twilio -related environment variables that will be needed by the web application:

    $ cd
    $ <edit> .bashrc
    Example1: vi .bashrc
    Example2: nano .bashrc

If you're not familiar with the VI/VIM editor then I suggest that you use Nano.

Add the following to the bottom of the .bashrc file.  The account SID and auth token are available via the Dashboard on Twilio.  The API key is available after you generate a Python project in Twilio.  Go to Settings --> API Keys.

The `MY_PHONE_NUMBER` environment variable must be set to the phone number of a phone that you have in your possession and **verified** through Twilio.

    export TWILIO_ACCOUNT_SID=<account SID from Twilio, no quotes>
    export TWILIO_AUTH_TOKEN=<auth token from Twilio, no quotes>
    export TWILIO_API_KEY=<generated API key SID from Twilio, no quotes>
    export TWILIO_API_SECRET=<generated API secret from Twilio, no quotes>
    export TWILIO_PHONE_NUMBER=<Twilio phone number, e.g. +14045551212, no quotes>
    export MY_PHONE_NUMBER=<Personal phone number, e.g. +14045551212, no quotes>

Example:

    export TWILIO_ACCOUNT_SID=AC11223344556677889900aabbccddeeff
    export TWILIO_AUTH_TOKEN=01234567890abcdef01234567890abcdef
    export TWILIO_API_KEY=SK01234567890abcdef1122334455667788
    export TWILIO_API_SECRET=AbccdEFghijkl0123456789MNOpqrstu
    export TWILIO_PHONE_NUMBER=+14045551212
    export MY_PHONE_NUMBER=+17705551212

Save the file then run the following command to apply the changes:

    $ source .bashrc

### Twilio CLI configuration
Do the following to enable Twilio CLI command autocompletion:

    $ cd
    $ twilio autocomplete bash
    $ printf "$(twilio autocomplete:script bash)" >> ~/.bashrc; source ~/.bashrc

### Test SMS Messaging
References:
- [Twilio SMS Python Quickstart](https://www.twilio.com/docs/sms/quickstart/python)

Do the following to test the ability to send a test message from the Raspberry Pi.  Refer to the above reference for additional details on sending and receiving SMS messages using Twilio.

    $ cd /var/www/sms/
    $ . bin/activate
    (sms) $ sudo cp ~/auto-event-picture-collector/send_sms.py .
    (sms) $ python send_sms.py

A text message will be sent to the phone number configured as `MY_PHONE_NUMBER` above.

Do the following to setup a simple Flask app to receive text messages:

    $ cd /var/www/sms/
    $ . bin/activate
    (sms) $ sudo cp ~/auto-event-picture-collector/receive_sms.py .
    (sms) $ python receive_sms.py

Open a 2nd SSH (or Terminal) session and do the following.  This will setup an ngrok session automatically and register it with Twilio.  The ngrok session will work for only eight hours for free.  A paid account is necessary to maintain  session indefinitely.

    $ twilio phone-numbers:update "<Twilio phone number>" --sms-url=http://localhost:5000/sms

Example:

    $ twilio phone-numbers:update "+17705551212" --sms-url=http://localhost:5000/sms

Using the phone configured as `MY_PHONE_NUMBER` send a text message to your Twilio phone number.  You will receive a response text message if everything is setup correctly.

### Test SMS Messaging via Full Web Application Stack
Do the following to test SMS messaging through the full web application stack setup previously:

    $ cd /var/www/sms/
    $ . bin/activate
    (sms) $ sudo mv receive_sms.py sms.py
    (sms) $ sudo systemctl restart emperor.uwsgi.service

Setup an ngrok session using the Twilio CLI.  Note the change in local port from 5000 to 80.

    $ twilio phone-numbers:update "<Twilio phone number" --sms-url=http://localhost:80/sms

Using the phone configured as `MY_PHONE_NUMBER` send a text message to your Twilio phone number.  You should receive a response text message like before.

NOTE: a default route is also setup in the test receive_sms.py script which means that you can still access the local web server from another device on the LAN by navigating to the local IP address of the Reaspberry Pi from a web browser.

## Setup Event Server
Setup the event server to collect pictures now that both the persistent full stack web application and Twilio are working.

    $ sudo cp ~/auto-event-picture-collector/event_server.py /var/www/sms/sms.py
    $ sudo systemctl stop emperor.uwsgi.service
    $ sudo systemctl edit emperor.uwsgi.service

Add the following to the `override.conf` file that will be created in the `/etc/systemd/system/emperor.uwsgi.service.d
` directory:

    [Service]
    Environment="TWILIO_ACCOUNT_SID=<account SID from Twilio>"
    Environment="TWILIO_AUTH_TOKEN=<auth token from Twilio>"
    Environment="TWILIO_API_KEY=<generated API key SID from Twilio>"
    Environment="TWILIO_API_SECRET=<generated API secret from Twilio>"
    Environment="TWILIO_PHONE_NUMBER=<Twilio phone number, e.g. +14045551212>"
    Environment="MY_PHONE_NUMBER=<Personal phone number, e.g. +14045551212>"

Example:

    [Service]
    Environment="TWILIO_ACCOUNT_SID=AC11223344556677889900aabbccddeeff"
    Environment="TWILIO_AUTH_TOKEN=01234567890abcdef01234567890abcdef"
    Environment="TWILIO_API_KEY=SK01234567890abcdef1122334455667788"
    Environment="TWILIO_API_SECRET=AbccdEFghijkl0123456789MNOpqrstu"
    Environment="TWILIO_PHONE_NUMBER=+14045551212"
    Environment="MY_PHONE_NUMBER=+17705551212"

Reload and Restart uWSGI:

    $ sudo systemctl start emperor.uwsgi.service
    $ sudo systemctl daemon-reload
    $ sudo systemctl restart emperor.uwsgi.service

Setup ngrok:

    $ twilio phone-numbers:update "<Twilio phone number" --sms-url=http://localhost:80/sms

## Persist Twilio Webhook
Make the Twilio webhook initialization persistent:

    $ sudo cp ~/auto-event-picture-collector/twilio.webhook.service /lib/systemd/system/
    $ cp ~/auto-event-picture-collector/twilio_webhook_init.py /home/pi/

Edit the `twilio_webhook_init.py` file if necessary to modify the version number for nodejs, then start and verify the service.

    $ sudo systemctl start twilio.webhook.service
    $ systemctl status twilio.webhook.service

Enable the service to run at bootup:

    $ sudo systemctl enable twilio.webhook.service

Setup environment variable.

    $ sudo systemctl stop twilio.webhook.service
    $ sudo systemctl edit twilio.webhook.service

Add the following to the `override.conf` file that will be created in the `/etc/systemd/system/twilio.webhook.service.d` directory:

    [Service]
    Environment="TWILIO_ACCOUNT_SID=<account SID from Twilio>"
    Environment="TWILIO_AUTH_TOKEN=<auth token from Twilio>"
    Environment="TWILIO_API_KEY=<generated API key SID from Twilio>"
    Environment="TWILIO_API_SECRET=<generated API secret from Twilio>"
    Environment="TWILIO_PHONE_NUMBER=<Twilio phone number, e.g. +14045551212>"
    Environment="MY_PHONE_NUMBER=<Personal phone number, e.g. +14045551212>"

Example:

    [Service]
    Environment="TWILIO_ACCOUNT_SID=AC11223344556677889900aabbccddeeff"
    Environment="TWILIO_AUTH_TOKEN=01234567890abcdef01234567890abcdef"
    Environment="TWILIO_API_KEY=SK01234567890abcdef1122334455667788"
    Environment="TWILIO_API_SECRET=AbccdEFghijkl0123456789MNOpqrstu"
    Environment="TWILIO_PHONE_NUMBER=+14045551212"
    Environment="MY_PHONE_NUMBER=+17705551212"

Reload and Restart uWSGI:

    $ sudo systemctl start emperor.uwsgi.service
    $ sudo systemctl daemon-reload
    $ sudo systemctl restart emperor.uwsgi.service

### Test Web Server Persistence
Reboot the Raspberry Pi using `sudo reboot now` then check the status of the twilio.webhook.service.

    $ sudo systemctl status emperor.uwsgi.service

Next, send a text message with contents of "status" from the phone verified by Twilio to your Twilio phone number.  Verify that a response is received.

## Setup Slideshow Application
### Install Tkinter
Do the following to install Tkinter.  Modify the Python version number below as needed.  Note that the Python3 installation is also updated to pull in the needed libraries.

    $ cd
    $ sudo apt update
    $ sudo apt install tk
    $ sudo apt install tk-dev
    $ cd python-source/Python-3.8.1/
    $ ./configure --prefix=/usr/local/opt/python-3.8.1
    $ make
    $ sudo make install

### Install Pillow

    $ cd /var/www/sms/
    $ . bin/activate
    (sms) $ sudo bin/pip install pillow

### Install Slideshow Application
TBD
## Disable Raspberry Pi Screensaver
Disable the screensaver on the Raspberry Pi to avoid having the screen go blank while displaying captured pictures:

Edit the `/etc/xdg/lxsession/LXDE-pi/autostart` file.

To disable the screensaver on a Raspberry Pi 3B+ or earlier add the following commands to the `autostart` file:

    @xset s off
    @xset -dpms

To disable the screensaver on a Raspberry Pi 4B or (possibly) later add the following commands to the `autostart` file:

    @xset s off
    @xset dpms 0 0 0
