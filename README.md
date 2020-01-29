# auto-event-picture-collector
Receive MMS messages using a Twilio number by running a web server on a Raspberry Pi then get picture(s) attached and display them on a connected TV.

# Installation and Setup
## Raspberry Pi Image Setup
References:
- [Raspbian Full Desktop image] (https://www.raspberrypi.org/downloads/raspbian/)
- [Etcher] (https://www.balena.io/etcher/)

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
Under the "System" tab of the Raspberry Pi configuration tool modify the "Hostname" (e.g. EventServer) to make the system easier to identify on the network, especially if you have multiple Raspberry Pi's running on your network like I do.

### SSH
Under the "Interfaces" tab enable SSH.

### VNC (optional)
Under the "Interfaces" tab enable VNC if you like to use VNC.

After all configuration changes are made reboot the Raspberry Pi as instructed.
