# Telegram-control-torrent
The Telegram Bot can control Deluge Torrent client

## How to Use
### Install package
Two packages (deluged, deluge-console) should be installed.
For more details: http://deluge-torrent.org/
```bash
$sudo apt-get install deluged, deluge-console
```
### Write setting.json

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
* token
The token is a string along the lines of 110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw that will be required to authorize the bot and send requests to the Bot API.
* valid_users
The user that is list up in valid_users can communicate with the telegram bot.
Every Telegram user has own id string.
