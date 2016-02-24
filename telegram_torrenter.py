#-*- coding: utf-8 -*-
import sys
import os
import feedparser
import telepot
import subprocess
import json
from telepot.delegate import per_chat_id, create_open
reload(sys)
sys.setdefaultencoding('utf-8')
CONFIG_FILE = 'setting.json'

################################################################################
# 
# DelugeAgent
# 
#  apt-get install deluge-console (for debian, ubuntu)
# 
class DelugeAgent:
    def downloadFromMagnet(self, magnet):
        os.system("deluge-console add " + magnet)

    def getCurrentList(self):
        return os.popen('deluge-console info').read()

    def filterCompletedList(self, result):
        outString = ''
        resultlist = result.split('\n \n')
        completedlist = []
        for entry in resultlist:
            title = entry[entry.index('Name:')+6:entry.index('ID:')-1]
            status = entry[entry.index('State:')+7:entry.index('Speed:')-1]
            progress = ''
            if status == 'Seeding Up':
                completedlist.append(entry[entry.index('ID:')+4:entry.index('State:')-1])
            elif status == 'Downloading Down':
                progress = entry[entry.index('Progress:')+10:entry.index('% [')+1]
            outString += '이름: '+title+'\n' + '상태:' + status + '\n'
            if progress:
                outString += '진행율:' + progress + '\n'
            outString += '\n'
        return (outString, completedlist)

    def removeFromList(self, id):
        os.system("deluge-console del " + id)


################################################################################
# 
# TransmissionAgent
# 
#  apt-get install transmission-cli (for debian, ubuntu)
# 
class TransmissionAgent:
    def __init__(self):
        transmissionCmd = 'transmission-remote '
        if TRANSMISSION_USER:
            transmissionCmd = transmissionCmd + '-n ' + TRANSMISSION_USER
            if TRANSMISSION_PASSWORD:
                transmissionCmd = transmissionCmd + ':' + TRANSMISSION_PASSWORD
            transmissionCmd = transmissionCmd + ' '
        if TRANSMISSION_PORT:
            transmissionCmd = transmissionCmd + '-p ' + TRANSMISSION_PORT + ' '
        self.transmissionCmd = transmissionCmd

    def downloadFromMagnet(self, magnet):
        os.system(self.transmissionCmd + '-a ' + magnet)

    def getCurrentList(self):
        return os.popen(self.transmissionCmd + '-l').read()

    def filterCompletedList(self, result):
        outString = ''
        resultlist = result.split('\n')
        titlelist = resultlist[0]
        resultlist = resultlist[1:-2]
        completedlist = []
        for entry in resultlist:
            title = entry[titlelist.index('Name'):].strip()
            status = entry[titlelist.index('Status'):titlelist.index('Name')-1].strip()
            progress = entry[titlelist.index('Done'):titlelist.index('Done')+4].strip()
            if progress == '100%':
                titleid = entry[titlelist.index('ID'):titlelist.index('Done')-1].strip()
                completedlist.append(titleid)
            outString += '이름: '+title+'\n' + '상태:' + status + '\n'
            if progress:
                outString += '진행율:' + progress + '\n'
            outString += '\n'
        return (outString, completedlist)

    def removeFromList(self, id):
        os.system(self.transmissionCmd + '-t '+ id + ' -r')

################################################################################
#
# Main Torrenter
#
#  Messange Handler for Telegram Bot
#
class Torrenter(telepot.helper.ChatHandler):
    YES = '1. OK'
    NO = '2. NO'
    MENU0 = '홈으로'
    MENU1 = '1. 토렌트 검색'
    MENU1_1 = '키워드 받기'
    MENU1_2 = '토렌트 선택'
    MENU2 = '2. 토렌트 리스트'
    rssUrl = """https://torrentkim1.net/bbs/rss.php?k="""
    GREETING = "안녕하세요. 메뉴를 선택해주세요."
    SubtitlesLocation = '' # please input your subtitle location to save subtitle files

    mode =''
    navi = feedparser.FeedParserDict()
    completedlist = []

    def __init__(self, seed_tuple, timeout):
        super(Torrenter, self).__init__(seed_tuple, timeout)
        self.agent = self.createAgent(AGENT_TYPE)

    def createAgent(self, agentType):
        if agentType == 'deluge':
            return DelugeAgent()
        if agentType == 'transmission':
            return TransmissionAgent()
        raise('invalid torrent client')
        return None

    def open(self, initial_msg, seed):
        self.menu()

    def menu(self):
        mode =''
        show_keyboard = {'keyboard': [[self.MENU1], [self.MENU2], [self.MENU0]]}
        self.sender.sendMessage(self.GREETING, reply_markup=show_keyboard)

    def yes_or_no(self, comment):
        show_keyboard = {'keyboard': [[self.YES, self.NO], [self.MENU0]]}
        self.sender.sendMessage(comment, reply_markup=show_keyboard)

    def tor_get_keyword(self):
        self.mode = self.MENU1_1
        self.sender.sendMessage('검색 키워드를 입력하세요.')

    def put_menu_button(self, l):
        menulist = [self.MENU0]
        l.append(menulist)
        return l

    def tor_search(self,keyword):
        self.mode=''
        self.sender.sendMessage('토렌트 검색중..')
        self.navi = feedparser.parse(self.rssUrl+keyword)

        outList = []
        if not self.navi.entries:
            self.sender.sendMessage('검색결과가 없습니다. 다시 입력하세요.')
            self.mode=self.MENU1_1
            return

        for (i,entry) in enumerate(self.navi.entries):
            if i == 10: break
            title = str(i+1) + ". " + entry.title

            templist = []
            templist.append(title)
            outList.append(templist)

        show_keyboard = {'keyboard': self.put_menu_button(outList)}
        self.sender.sendMessage('아래에서 선택하세요.', reply_markup=show_keyboard)
        self.mode=self.MENU1_2

    def tor_download(self, selected):
        self.mode=''
        print ("tor_sel")
        index = int(selected.split('.')[0]) - 1
        print ("index", index)
        magnet = self.navi.entries[index].link
        print ("magnet", magnet)
        #os.system("deluge-console add " + magnet)
        self.agent.downloadFromMagnet(magnet)
        self.sender.sendMessage('다운로드를 시작합니다.')
        self.navi.clear()
        self.menu()

    def tor_show_list(self):
        self.mode=''
        self.sender.sendMessage('토렌트 리스트를 확인중..')
        outString = ''
        #result = os.popen('deluge-console info').read()
        result = self.agent.getCurrentList()
        if not result:
            self.sender.sendMessage('진행중인 토렌트가 없습니다.')
            self.menu()
            return
        (outString, completedlist) = self.agent.filterCompletedList(result)
        self.completedlist = completedlist

        self.sender.sendMessage(outString)
        self.tor_del_list()

    def tor_del_list(self):
        self.mode=''
        self.sender.sendMessage('완료된 항목을 자동 정리중..')
        for id in self.completedlist:
            self.agent.removeFromList(id)
        self.sender.sendMessage('완료')
        self.menu()

    def handle_command(self, command):
        if command == self.MENU0:
            self.menu()
        elif command == self.MENU1:
            self.tor_get_keyword()
        elif command == self.MENU2:
            self.tor_show_list()
        elif self.mode == self.MENU1_1: # Get Keyword
            self.tor_search(command)
        elif self.mode == self.MENU1_2: # Download Torrent
            self.tor_download(command)

    def handle_smi(self, file_id, file_name):
        try:
            bot.downloadFile(file_id, self.SubtitlesLocation + file_name)
        except Exception as inst: print inst
        self.sender.sendMessage('자막 파일을 저장했습니다.')
        pass

    def on_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance2(msg)
        #Check ID
        if not chat_id in VALID_USERS:
            print("Permission Denied")
            return

        if content_type is 'text':
            self.handle_command(unicode(msg['text']))
            return

        if content_type is 'document':
            file_name = msg['document']['file_name']
            if file_name[-3:] == 'smi':
                file_id = msg['document']['file_id']
                self.handle_smi(file_id, file_name)
                return
            self.sender.sendMessage('인식할 수 없는 파일입니다.')
            return

        print ("E")
        self.sender.sendMessage('인식하지 못했습니다')
    def on_close(self, exception):
        pass

def parseConfig(filename):
    f = open(filename, 'r')
    js = json.loads(f.read())
    f.close()
    return js

def getConfig(config):
    global TOKEN
    global AGENT_TYPE
    global VALID_USERS
    TOKEN = config['common']['token']
    AGENT_TYPE = config['common']['agent_type']
    VALID_USERS = config['common']['valid_users']
    if AGENT_TYPE == 'transmission':
        global transmission_user
        global transmission_password
        global transmission_port
        TRANSMISSION_USER = config['for_transmission']['transmission_user']
        TRANSMISSION_PASSWORD = config['for_transmission']['transmission_password']
        TRANSMISSION_PORT = config['for_transmission']['transmission_port']

config = parseConfig(CONFIG_FILE)
if not bool(config):
    print ("Err: Setting file is not found")
    exit()
getConfig(config)
bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(Torrenter, timeout=120)),
])
bot.notifyOnMessage(run_forever=True)
