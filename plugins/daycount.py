# -*- coding: utf-8 -*-
import copy
import datetime

startday = datetime.datetime.strptime('2019-06-24', '%Y-%m-%d')

def onServerInfo(server, info):
  if info.isPlayer == 1:
    if info.content.startswith('!!day') and not info.content.startswith('!!daytime'):
      server.say('今天是這個伺服器開服的第' + getday() + '天')

def on_info(server, info):
  info2 = copy.deepcopy(info)
  info2.isPlayer = info2.is_player
  onServerInfo(server, info2)

def getday():
  now = datetime.datetime.now()
  output = now - startday
  return str(output.days)

def on_load(server, old):
  server.add_help_message('!!day', '顯示今天是開服的第幾天')
