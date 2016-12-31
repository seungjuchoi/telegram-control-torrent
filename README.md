# Telegram-control-transmission
The Telegram Bot can control a Transmission as Torrent machine

## How to Use
### Install Transmission 
```bash
$sudo apt-get install transmission-cli transmission-common transmission-daemon
```
For more details: https://transmissionbt.com/download/

### Write setting.json
ex)
```json
{
  "common": {
    "token": "110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw",
    "valid_users": [
      123456789,
      123456789
    ],
    "agent_type": "transmission"
  }
}
```
* token: The token is a string along the lines of 110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw that will be required to authorize the bot and send requests to the Bot API.
* valid_users: The user that is list up in valid_users can communicate with the telegram bot.
Every Telegram user has own id string. put your telegram id into that

### Install python package
```bash
pip3 install -r pip-requirements.txt
```
### Run
```bash
python3 telegram_torrent.py
```
