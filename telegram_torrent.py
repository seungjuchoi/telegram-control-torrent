#!/usr/bin/python3
import sys
import os
import feedparser
import telepot
import json
import random
import string
from urllib import parse
from apscheduler.schedulers.background import BackgroundScheduler
from telepot.delegate import per_chat_id, create_open, pave_event_space

CONFIG_FILE = 'setting.json'


class DelugeAgent:

    def __init__(self, sender):
        self.STATUS_SEED = 'Seeding'
        self.STATUS_DOWN = 'Downloading'
        self.STATUS_ERR = 'Error'  # Need Verification
        self.weightList = {}
        self.sender = sender

    def download(self, item):
        os.system("deluge-console add " + item)

    def getCurrentList(self):
        return os.popen('deluge-console info').read()

    def printElement(self, e):
        outString = 'NAME: ' + e['title'] + \
            '\n' + 'STATUS: ' + e['status'] + '\n'
        outString += 'PROGRESS: ' + e['progress'] + '\n'
        outString += '\n'
        return outString

    def parseList(self, result):
        if not result:
            return
        outList = []
        for entry in result.split('\n \n'):
            title = entry[entry.index('Name:') + 6:entry.index('ID:') - 1]
            status = entry[entry.index('State:'):].split(' ')[1]
            ID = entry[entry.index('ID:') + 4:entry.index('State:') - 1]
            if status == self.STATUS_DOWN:
                progress = entry[entry.index(
                    'Progress:') + 10:entry.index('% [') + 1]
            else:
                progress = '0.00%'
            element = {'title': title, 'status': status,
                       'ID': ID, 'progress': progress}
            outList.append(element)
        return outList

    def isOld(self, ID, progress):
        """weightList = {ID:[%,w],..}"""
        if ID in self.weightList:
            if self.weightList[ID][0] == progress:
                self.weightList[ID][1] += 1
            else:
                self.weightList[ID][0] = progress
                self.weightList[ID][1] = 1
            if self.weightList[ID][1] > 3:
                return True
        else:
            self.weightList[ID] = [progress, 1]
            return False
        return False

    def check_torrents(self):
        currentList = self.getCurrentList()
        outList = self.parseList(currentList)
        if not bool(outList):
            self.sender.sendMessage('The torrent List is empty')
            scheduler.remove_all_jobs()
            self.weightList.clear()
            return
        for e in outList:
            if e['status'] == self.STATUS_SEED:
                self.sender.sendMessage(
                    'Download completed: {0}'.format(e['title']))
                self.removeFromList(e['ID'])
            elif e['status'] == self.STATUS_ERR:
                self.sender.sendMessage(
                    'Download canceled (Error): {0}\n'.format(e['title']))
                self.removeFromList(e['ID'])
            else:
                if self.isOld(e['ID'], e['progress']):
                    self.sender.sendMessage(
                        'Download canceled (pending): {0}\n'.format(e['title']))
                    self.removeFromList(e['ID'])
        return

    def removeFromList(self, ID):
        if ID in self.weightList:
            del self.weightList[ID]
        os.system("deluge-console del " + ID)


class TransmissionAgent:

    def __init__(self, sender):
        self.STATUS_SEED = 'Seeding'
        self.STATUS_ERR = 'Error'  # Need Verification
        self.weightList = {}
        self.sender = sender
        cmd = 'transmission-remote '
        if TRANSMISSION_ID_PW:
            cmd = cmd + '-n ' + TRANSMISSION_ID_PW + ' '
        else:
            cmd = cmd + '-n ' + 'transmission:transmission' + ' '
        self.transmissionCmd = cmd

    def download(self, magnet):
        if TRANSMISSION_PORT:
            pcmd = '-p ' + TRANSMISSION_PORT + ' '
        else:
            pcmd = ''
        if DOWNLOAD_PATH:
            wcmd = '-w ' + DOWNLOAD_PATH + ' '
        else:
            wcmd = ''
        os.system(self.transmissionCmd + pcmd + wcmd + '-a ' + magnet)

    def getCurrentList(self):
        l = os.popen(self.transmissionCmd + '-l').read()
        rowList = l.split('\n')
        if len(rowList) < 4:
            return
        else:
            return l

    def printElement(self, e):
        outString = 'NAME: ' + e['title'] + \
            '\n' + 'STATUS: ' + e['status'] + '\n'
        outString += 'PROGRESS: ' + e['progress'] + '\n'
        outString += '\n'
        return outString

    def parseList(self, result):
        if not result:
            return
        outList = []
        resultlist = result.split('\n')
        titlelist = resultlist[0]
        resultlist = resultlist[1:-2]
        for entry in resultlist:
            title = entry[titlelist.index('Name'):].strip()
            status = entry[titlelist.index(
                'Status'):titlelist.index('Name') - 1].strip()
            progress = entry[titlelist.index(
                'Done'):titlelist.index('Done') + 4].strip()
            id_ = entry[titlelist.index(
                'ID'):titlelist.index('Done') - 1].strip()
            if id_[-1:] == '*':
                id_ = id_[:-1]
            element = {'title': title, 'status': status,
                       'ID': id_, 'progress': progress}
            outList.append(element)
        return outList

    def removeFromList(self, ID):
        if ID in self.weightList:
            del self.weightList[ID]
        os.system(self.transmissionCmd + '-t ' + ID + ' -r')

    def isOld(self, ID, progress):
        """weightList = {ID:[%,w],..}"""
        if ID in self.weightList:
            if self.weightList[ID][0] == progress:
                self.weightList[ID][1] += 1
            else:
                self.weightList[ID][0] = progress
                self.weightList[ID][1] = 1
            if self.weightList[ID][1] > 3:
                return True
        else:
            self.weightList[ID] = [progress, 1]
            return False
        return False

    def check_torrents(self):
        currentList = self.getCurrentList()
        outList = self.parseList(currentList)
        if not bool(outList):
            self.sender.sendMessage('The torrent List is empty')
            scheduler.remove_all_jobs()
            self.weightList.clear()
            return
        for e in outList:
            if e['status'] == self.STATUS_SEED:
                self.sender.sendMessage(
                    'Download completed: {0}'.format(e['title']))
                self.removeFromList(e['ID'])
            elif e['status'] == self.STATUS_ERR:
                self.sender.sendMessage(
                    'Download canceled (Error): {0}\n'.format(e['title']))
                self.removeFromList(e['ID'])
            else:
                if self.isOld(e['ID'], e['progress']):
                    self.sender.sendMessage(
                        'Download canceled (pending): {0}\n'.format(e['title']))
                    self.removeFromList(e['ID'])
        return


class Torrenter(telepot.helper.ChatHandler):
    YES = '<OK>'
    NO = '<NO>'
    MENU0 = 'HOME'
    MENU1 = 'SEARCH TORRENT'
    MENU1_1 = 'INPUT A WORD'
    MENU1_2 = 'CHOOSE AN ITEM'
    MENU2 = 'TORRENT LIST'
    rssUrl = """https://torrentkim1.net/bbs/rss.php?k="""
    GREETING = "SELECT MENU"
    global scheduler
    DownloadFolder = ''  # Option: Input your subtitle location to save subtitle files,

    mode = ''
    navi = feedparser.FeedParserDict()

    def __init__(self, *args, **kwargs):
        super(Torrenter, self).__init__(*args, **kwargs)
        self.agent = self.createAgent(AGENT_TYPE)

    def createAgent(self, agentType):
        if agentType == 'deluge':
            return DelugeAgent(self.sender)
        if agentType == 'transmission':
            return TransmissionAgent(self.sender)
        raise ('invalid torrent client')

    def open(self, initial_msg, seed):
        self.menu()

    def menu(self):
        mode = ''
        show_keyboard = {'keyboard': [
            [self.MENU1], [self.MENU2], [self.MENU0]]}
        self.sender.sendMessage(self.GREETING, reply_markup=show_keyboard)

    def yes_or_no(self, comment):
        show_keyboard = {'keyboard': [[self.YES, self.NO], [self.MENU0]]}
        self.sender.sendMessage(comment, reply_markup=show_keyboard)

    def tor_get_keyword(self):
        self.mode = self.MENU1_1
        self.sender.sendMessage('Enter a Keyword')

    def put_menu_button(self, l):
        menulist = [self.MENU0]
        l.append(menulist)
        return l

    def tor_search(self, keyword):
        self.mode = ''
        self.sender.sendMessage('Searching torrent..')
        self.navi = feedparser.parse(self.rssUrl + parse.quote(keyword))

        outList = []
        if not self.navi.entries:
            self.sender.sendMessage('Sorry, No results')
            self.mode = self.MENU1_1
            return

        for (i, entry) in enumerate(self.navi.entries):
            if i == 10:
                break
            title = str(i + 1) + ". " + entry.title

            templist = []
            templist.append(title)
            outList.append(templist)

        show_keyboard = {'keyboard': self.put_menu_button(outList)}
        self.sender.sendMessage('Choose one from below',
                                reply_markup=show_keyboard)
        self.mode = self.MENU1_2

    def tor_download(self, selected):
        self.mode = ''
        index = int(selected.split('.')[0]) - 1
        magnet = self.navi.entries[index].link
        self.agent.download(magnet)
        self.sender.sendMessage('Start Downloading')
        self.navi.clear()
        if not scheduler.get_jobs():
            scheduler.add_job(self.agent.check_torrents, 'interval', minutes=1)
        self.menu()

    def tor_show_list(self):
        self.mode = ''
        self.sender.sendMessage('Let me check the torrent list..')
        result = self.agent.getCurrentList()
        if not result:
            self.sender.sendMessage('The torrent list is empty')
            self.menu()
            return
        outList = self.agent.parseList(result)
        for e in outList:
            self.sender.sendMessage(self.agent.printElement(e))

    def handle_command(self, command):
        if command == self.MENU0:
            self.menu()
        elif command == self.MENU1:
            self.tor_get_keyword()
        elif command == self.MENU2:
            self.tor_show_list()
        elif self.mode == self.MENU1_1:  # Get Keyword
            self.tor_search(command)
        elif self.mode == self.MENU1_2:  # Download Torrent
            self.tor_download(command)

    def handle_smifile(self, file_id, file_name):
        try:
            self.sender.sendMessage('Saving subtitle file..')
            bot.download_file(file_id, self.DownloadFolder + file_name)
        except Exception as inst:
            self.sender.sendMessage('ERORR: {0}'.format(inst))
            return
        self.sender.sendMessage('Done')

    def handle_seedfile(self, file_id, file_name):
        try:
            self.sender.sendMessage('Saving torrent file..')
            generated_file_path = self.DownloadFolder + \
                "".join(random.sample(string.ascii_letters, 8)) + ".torrent"
            bot.download_file(file_id, generated_file_path)
            self.agent.download(generated_file_path)
            os.system("rm " + generated_file_path)
            if not scheduler.get_jobs():
                scheduler.add_job(self.agent.check_torrents,
                                  'interval', minutes=1)
        except Exception as inst:
            self.sender.sendMessage('ERORR: {0}'.format(inst))
            return
        self.sender.sendMessage('Start Downloading')

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        # Check ID
        if not chat_id in VALID_USERS:
            print("Permission Denied")
            return

        if content_type is 'text':
            self.handle_command(msg['text'])
            return

        if content_type is 'document':
            file_name = msg['document']['file_name']
            if file_name[-3:] == 'smi':
                file_id = msg['document']['file_id']
                self.handle_smifile(file_id, file_name)
                return
            if file_name[-7:] == 'torrent':
                file_id = msg['document']['file_id']
                self.handle_seedfile(file_id, file_name)
                return
            self.sender.sendMessage('Invalid File')
            return

        self.sender.sendMessage('Invalid File')

    def on_close(self, exception):
        pass


def parseConfig(filename):
    path = os.path.dirname(os.path.realpath(__file__)) + '/' + filename
    f = open(path, 'r')
    js = json.loads(f.read())
    f.close()
    return js


def getConfig(config):
    global TOKEN
    global AGENT_TYPE
    global VALID_USERS
    global DOWNLOAD_PATH
    TOKEN = config['common']['token']
    AGENT_TYPE = config['common']['agent_type']
    VALID_USERS = config['common']['valid_users']
    DOWNLOAD_PATH = config['common']['download_path']
    if AGENT_TYPE == 'transmission':
        global TRANSMISSION_ID_PW
        global TRANSMISSION_PORT
        TRANSMISSION_ID_PW = config['transmission']['id_pw']
        TRANSMISSION_PORT = config['transmission']['port']


config = parseConfig(CONFIG_FILE)
if not bool(config):
    print("Err: Setting file is not found")
    exit()
getConfig(config)
scheduler = BackgroundScheduler()
scheduler.start()
bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, Torrenter, timeout=120),
])
bot.message_loop(run_forever='Listening ...')
