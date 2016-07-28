# Telegram-control-torrent
The Telegram Bot can control Deluge Torrent client

## Requirements
Two packages (deluged, deluge-console) that you can get in linux debian.
$sudo apt-get install deluged, deluge-console
You'd better check whether your deluge torrent system is working well before applying this system
For more details: http://deluge-torrent.org/


## How to Setting
* token
The token is a string along the lines of 110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw that will be required to authorize the bot and send requests to the Bot API.
* valid_users
The user that is list up in valid_users can communicate with the telegram bot.
Every Telegram user has own id string.

The below is example code.
```json
{
  "common": {
    "token": "110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw",
    "valid_users": [
      123456789,
      123456789
    ],
    "agent_type": "deluge"
  }
}
```
