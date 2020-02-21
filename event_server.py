'''
Main event server script
'''
import requests
import pprint
import os
import subprocess
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse


DOWNLOAD_DIRECTORY = '/home/pi/Pictures'
TRASH_DIRECTORY = '/home/pi/Pictures/trash'
USB_DIRECTORY = '/media/pi'
CURRENT_WIFI_CONFIG_FILE = '/etc/wpa_supplicant/wpa_supplicant.conf'
NEW_WIFI_CONFIG_FILE = '/home/pi/wifi_files/wpa_supplicant.conf.event'
PHOTO_EXTS = ('.jpg', '.jpeg', '.bmp', '.png')
VIDEO_EXTS = ('.3gpp', '.mov', '.m4v')
MY_PERSONAL_PHONE_NUMBER = os.environ["MY_PHONE_NUMBER"]

# Global state info
# Wi-Fi setup state transitions
WIFI_STATE_IDLE = 0        # IDLE --> get "wifi" command --> WIFI_STATE_SSID
WIFI_STATE_SSID = 1        # waiting for SSID --> get SSID --> WIFI_STATE_PASSPHRASE
WIFI_STATE_PASSPHRASE = 2  # waiting for passphrase --> get passphrase --> WIFI_STATE_IDLE

wifi_setup_state = WIFI_STATE_IDLE
wifi_ssid = ""
wifi_passphrase = ""

# Incoming message fields
SMS_FROM = 'From'
SMS_BODY = 'Body'
SMS_MSG_SID = 'MessageSid'
SMS_NUM_MEDIA = 'NumMedia'
SMS_MEDIA_TYPE_BASE = 'MediaContentType'
SMS_MEDIA_URL_BASE = 'MediaUrl'

app = Flask(__name__)
debug_app = True
pretty_print = False

'''
Example text message received with no pictures:
{'AccountSid': 'AC12345abcde12345abcde12345abcde12',
 'ApiVersion': '2010-04-01',
 'Body': 'Test message 3!',
 'From': '+14045551212',
 'FromCity': 'ATLANTA',
 'FromCountry': 'US',
 'FromState': 'GA',
 'FromZip': '30360',
 'MessageSid': 'SM574821705f1458882f283ab5d5cdee12',
 'NumMedia': '0',
 'NumSegments': '1',
 'SmsMessageSid': 'SM574821705f1458882f283ab5d5cdee12',
 'SmsSid': 'SM574821705f1458882f283ab5d5cdee12',
 'SmsStatus': 'received',
 'To': '+17705551212',
 'ToCity': 'FORT LAUDERDALE',
 'ToCountry': 'US',
 'ToState': 'FL',
 'ToZip': '33301'}

Example text message received with one picture and no text:
{'AccountSid': 'AC12345abcde12345abcde12345abcde12',
 'ApiVersion': '2010-04-01',
 'Body': '',
 'From': '+14045551212',
 'FromCity': 'ATLANTA',
 'FromCountry': 'US',
 'FromState': 'GA',
 'FromZip': '30360',
 'MediaContentType0': 'image/jpeg',
 'MediaUrl0': 'https://api.twilio.com/2010-04-01/Accounts/AC12345abcde12345abcde12345abcde12/Messages/MM7225452fbc89614affd898ce3797a32e/Media/ME1938946d1abb1b94c173b7ba82512790',
 'MessageSid': 'MM7225452fbc89614affd898ce3797a32e',
 'NumMedia': '1',
 'NumSegments': '1',
 'SmsMessageSid': 'MM7225452fbc89614affd898ce3797a32e',
 'SmsSid': 'MM7225452fbc89614affd898ce3797a32e',
 'SmsStatus': 'received',
 'To': '+17705551212',
 'ToCity': 'FORT LAUDERDALE',
 'ToCountry': 'US',
 'ToState': 'FL',
 'ToZip': '33301'}

Example text message received with two pictures and text:
{'AccountSid': 'AC12345abcde12345abcde12345abcde12',
 'ApiVersion': '2010-04-01',
 'Body': "Test multiple pics and quote '",
 'From': '+14045551212',
 'FromCity': 'ATLANTA',
 'FromCountry': 'US',
 'FromState': 'GA',
 'FromZip': '30360',
 'MediaContentType0': 'image/jpeg',
 'MediaContentType1': 'image/jpeg',
 'MediaUrl0': 'https://api.twilio.com/2010-04-01/Accounts/AC12345abcde12345abcde12345abcde12/Messages/MMc6d3e08fc6ceb273191e4728452193d3/Media/MEff0ab26db282c6d62e01edc5c68a8a3d',
 'MediaUrl1': 'https://api.twilio.com/2010-04-01/Accounts/AC12345abcde12345abcde12345abcde12/Messages/MMc6d3e08fc6ceb273191e4728452193d3/Media/MEef1319fd82876c44b5a09849d7cb4e09',
 'MessageSid': 'MMc6d3e08fc6ceb273191e4728452193d3',
 'NumMedia': '2',
 'NumSegments': '2',
 'SmsMessageSid': 'MMc6d3e08fc6ceb273191e4728452193d3',
 'SmsSid': 'MMc6d3e08fc6ceb273191e4728452193d3',
 'SmsStatus': 'received',
 'To': '+17705551212',
 'ToCity': 'FORT LAUDERDALE',
 'ToCountry': 'US',
 'ToState': 'FL',
 'ToZip': '33301'}
'''


def get_disk_space_used_str(files, directory, trash_files, trash_directory):
    files_disk_space = 0
    files_disk_space_str = '0'

    if not files and not trash_files:
        return files_disk_space_str

    for file in files:
        files_disk_space += os.path.getsize(os.path.join(directory, file))

    for file in trash_files:
        files_disk_space += os.path.getsize(os.path.join(trash_directory, file))

    # Convert to KB
    files_disk_space /= 1024

    if files_disk_space < 1000:
        files_disk_space_str = f'{files_disk_space:.2f}KB'
    else:
        # Convert to MB
        files_disk_space /=1024

        if files_disk_space < 1000:
            files_disk_space_str = f'{files_disk_space:.2f}MB'
        else:
            # Convert to GB
            files_disk_space /=1024
            files_disk_space_str = f'{files_disk_space:.2f}GB'

    return files_disk_space_str


@app.route("/")
def hello():
    return "Hello again from my web server!"


@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming with a simple text message."""
    global wifi_setup_state, wifi_ssid, wifi_passphrase

    resp = MessagingResponse()

    try:
        num_pics = int(request.values[SMS_NUM_MEDIA])
    except:
        print('Invalid NumMedia format in received message.')
        pprint.pprint(request.values)
        num_pics = 0

    if num_pics:
        if debug_app:
            print(f'Found {num_pics} pictures in message')

        for idx in range(num_pics):
            try:
                ext = '.' + request.values[SMS_MEDIA_TYPE_BASE + str(idx)].split('/')[-1]
            except:
                print(f'Could not extract MediaContentType from received message for index {idx}.')
                pprint.pprint(request.values)
                ext = '.png'

            # Use the message SID as the base for the filename
            # and the image type as extension
            tmp_filename = request.values[SMS_MSG_SID] + '_' + str(idx) + '.tmp'
            filename = request.values[SMS_MSG_SID] + '_' + str(idx) + ext

            # Save the image to a temporary file while it's downloading.
            with open(os.path.join(DOWNLOAD_DIRECTORY, tmp_filename), 'wb') as f:
               image_url = request.values[SMS_MEDIA_URL_BASE + str(idx)]
               f.write(requests.get(image_url).content)

            # Go ahead and make the image available now that's it's downloaded,
            # but don't overwrite an existing file.
            if os.path.exists(os.path.join(DOWNLOAD_DIRECTORY, filename)):
                i = 0

                while True:
                    test_filename = request.values[SMS_MSG_SID] + '_' + str(idx) + '_' + str(i) + ext

                    if os.path.exists(os.path.join(DOWNLOAD_DIRECTORY, test_filename)):
                        i += 1
                    else:
                        filename = test_filename
                        break

            os.rename(os.path.join(DOWNLOAD_DIRECTORY, tmp_filename),
                      os.path.join(DOWNLOAD_DIRECTORY, filename))

        if num_pics > 1:
            resp.message("Thanks for the images!")
        else:
            resp.message("Thanks for the image!")

        if debug_app and pretty_print:
            pprint.pprint(request.values)
    elif request.values[SMS_FROM] == MY_PERSONAL_PHONE_NUMBER:
        if debug_app:
            print('Received a command from the admin operator!!!')

        # Handle Wi-Fi setup first since credentials are case sensitive
        if wifi_setup_state != WIFI_STATE_IDLE:
            wifi_info = request.values[SMS_BODY].strip()

            if wifi_setup_state == WIFI_STATE_SSID:
                # Got SSID, get passphrase
                wifi_ssid = wifi_info
                wifi_setup_state = WIFI_STATE_PASSPHRASE
                resp.message("Passphrase?")
            elif wifi_setup_state == WIFI_STATE_PASSPHRASE:
                # Got passphrase, setup Wi-Fi config
                wifi_passphrase = wifi_info
                wifi_setup_state = WIFI_STATE_IDLE

                if os.path.isfile(CURRENT_WIFI_CONFIG_FILE):
                    with open(CURRENT_WIFI_CONFIG_FILE, "r") as current_config_file:
                        config_data = current_config_file.read()

                    config_data += '\n\n'
                    config_data += 'network={\n'
                    config_data += f'    ssid="{wifi_ssid}"\n'
                    config_data += f'    psk="{wifi_passphrase}"\n'
                    config_data += '    key_mgmt=WPA-PSK\n'
                    config_data += '}\n'

                    with open(NEW_WIFI_CONFIG_FILE, "w") as updated_config_file:
                        updated_config_file.write(config_data)

                    cmd = f'sudo cp {NEW_WIFI_CONFIG_FILE} {CURRENT_WIFI_CONFIG_FILE}'
                    subprocess.call(cmd, shell=True)
                    resp.message("Wi-Fi configured...issue reboot command")
                else:
                    resp.message("Can't find current Wi-Fi config file!")
            else:
                resp.message("Internal error: invalid Wi-Fi state!")

            return str(resp)

        command = request.values[SMS_BODY].lower().strip()

        if command == 'commands':
            resp_msg_str = ''
            resp_msg_str += 'status: get status\n'
            resp_msg_str += 'pause/resume: pause/resume pic display\n'
            resp_msg_str += 'ip: get IP addresses\n'
            resp_msg_str += 'reboot: reboot device\n'
            resp_msg_str += 'trash: move current pic to trash\n'
            resp_msg_str += 'wifi: setup Wi-Fi creds\n'
            resp_msg_str += 'backup: backup pics to USB\n'
            resp.message(resp_msg_str)
        elif command == 'wifi':
            wifi_setup_state = WIFI_STATE_SSID
            resp.message("Network name?")
        elif command == 'backup':
            # Copy all pictures to attached USB
            dir_items = os.listdir(USB_DIRECTORY)
            found_usb = False

            for item in dir_items:
                if os.path.isdir(os.path.join(USB_DIRECTORY, item)):
                    found_usb = True
                    break

            if found_usb:
                subprocess.call('touch /var/tmp2/backup_pics', shell=True)
                resp.message('Backing up pics to USB drive.  When picture display changes USB is ready...')
            else:
                resp.message('No USB attached!')
        elif command == 'ip':
            ip_address = subprocess.check_output("hostname -I", shell=True).decode('utf-8').replace(' ', '\n')
            resp.message(ip_address)
        elif command == 'reboot':
            subprocess.call('sudo reboot now', shell=True)
        elif command == 'pause':
            if debug_app:
                print('Pausing picture display...')

            subprocess.call('touch /var/tmp2/pause_pic', shell=True)
            resp.message('Picture display paused')
        elif command == 'resume':
            if debug_app:
                print('Resuming picture display...')

            subprocess.call('touch /var/tmp2/resume_pic', shell=True)
            resp.message('Picture display resumed')
        elif command == 'drop' or command == 'trash':
            if debug_app:
                print('Moving picture to trash...')

            subprocess.call('touch /var/tmp2/trash_pic', shell=True)
            resp.message('Picture moved to trash')
        elif command == 'status':
            resp_msg_str = ''

            pics = [file for file in os.listdir(DOWNLOAD_DIRECTORY) if file.endswith(PHOTO_EXTS)]
            trash_pics = [file for file in os.listdir(TRASH_DIRECTORY) if file.endswith(PHOTO_EXTS)]
            num_pics = len(pics) + len(trash_pics)
            pics_disk_space_str = get_disk_space_used_str(pics, DOWNLOAD_DIRECTORY,
                                                          trash_pics, TRASH_DIRECTORY)

            vids = [file for file in os.listdir(DOWNLOAD_DIRECTORY) if file.endswith(VIDEO_EXTS)]
            trash_vids = [file for file in os.listdir(TRASH_DIRECTORY) if file.endswith(VIDEO_EXTS)]
            num_vids = len(vids) + len(trash_vids)
            vids_disk_space_str = get_disk_space_used_str(vids, DOWNLOAD_DIRECTORY,
                                                          trash_vids, TRASH_DIRECTORY)

            usage_stats = os.statvfs(DOWNLOAD_DIRECTORY + "/")
            space_avail = usage_stats.f_bavail * usage_stats.f_frsize
            space_avail /= 1024**3

            resp_msg_str += f'Pics: {num_pics}\n'
            resp_msg_str += f'Videos: {num_vids}\n'
            resp_msg_str += f'Disk space avail: {space_avail:.2f}GB\n'
            resp_msg_str += f'Disk space used (pics): {pics_disk_space_str}\n'
            resp_msg_str += f'Disk space used (vids): {vids_disk_space_str}\n'
            resp.message(resp_msg_str)
        else:
            # TODO - add more commands
            if debug_app:
                print(f'Unknown command: "{command}"')
                pprint.pprint(request.values)
            resp.message('Unknown command.  Type "commands" for help.')
    else:
        if debug_app and pretty_print:
            pprint.pprint(request.values)
        resp.message("Try sending a picture message.")

    return str(resp)


if __name__ == "__main__":
    app.run(debug=debug_app)
