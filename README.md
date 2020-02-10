# auto-event-picture-collector
Receive MMS messages using a Twilio number by running a full stack web server on a Raspberry Pi then retrieve all pictures attached and display them on a connected TV.

Minimum required Python version: 3.8.0 (although earlier versions starting at 3.6 ***should*** work, but have not been tested)
# Installation and Setup
## Raspberry Pi Image Setup
References:
- [Raspbian Full Desktop image](https://www.raspberrypi.org/downloads/raspbian/)
- [Etcher](https://www.balena.io/etcher/)

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
## Upgrade Python3
This step is only necessary if the Raspberry Pi is not running the minimum required version of Python3.

Do the following to check the current version:

    $ python3 -V

If the current version of Python3 is earlier than the minimum required OR you would simply like to upgrade to the latest version then do the following:

    $ sudo apt update
    $ cd ~
    $ mkdir python-source
    $ cd python-source/

Do the following to get the URL to the latest Python3

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
