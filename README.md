# telegram-control-torrent
Telegram Bot can control Torrent system(deluge, transmission)
## For deluge
### Requirements
Two packages (deluged, deluge-console) that you can get in linux debian.
$sudo apt-get install deluged, deluge-console
You'd better check whether your deluge torrent system is working well or not before applying this system
for more details: http://deluge-torrent.org/
## For transmission
### Requirements
transmission-remote. You can get it from ***transmission-cli*** package in linux debian.
### Configuration
set **AGENT_TYPE** as ***transmission*** instead of ***deluge***
