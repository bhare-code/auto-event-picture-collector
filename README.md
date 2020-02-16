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
Do the following to configure the web server.  The default configuraiton for NGiNX

    (sms) $ cd /etc/nginx/sites-enabled/
    (sms) $ sudo rm default
    (sms) $ cd /var/www/sms/
    (sms) $ sudo cp ~/auto-event-picture-collector/sms_nginx.conf .
    (sms) $ sudo ln -s /var/www/sms/lab_app_nginx.conf /etc/nginx/conf.d/
