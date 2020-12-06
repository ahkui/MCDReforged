# coding=utf-8
from time import sleep
import re

help_msg = '''------ §aMCDR TPS測試附加元件幫助 §f------
§b!!tps help §f- §c顯示此幫助訊息
§b!!tps §f- §c測試伺服器的tps
§b!!tps [秒] §f- §c測試伺服器tps, [秒] 測試時間
--------------------------------'''


def on_info(server, info):
    if info.is_player == 1:
        if info.content.startswith('!!tps'):
            args = info.content.split(' ')
            if len(args) == 1:
                server.execute('debug start')
                sleep(1)
                server.execute('debug stop')
            elif args[1] == 'help':
                for line in help_msg.splitlines():
                    server.tell(info.player, line)
            elif len(args) == 2:
                time = int(args[1])
                server.execute('debug start')
                sleep(time)
                server.execute('debug stop')
    elif 'Stopped debug profiling after' in info.content:
        match = re.compile(r'[(](.*?)[)]', re.S)
        split = re.findall(match, info.content)[0].split(" ")[0]
        server.say("------ §a目前伺服器的TPS為 §e" + split + " §f------")

def on_load(server, info):
    server.add_help_message('!!tps help', 'TPS測試幫助')