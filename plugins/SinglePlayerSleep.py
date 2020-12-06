# -*- coding: utf-8 -*-

import time
import re
from utils.rtext import *
from plugins import PlayerInfoAPI as PlayerAPI
from plugins.ConfigAPI import Config

default_config = {
    'skip_wait_time': 10,
    'wait_before_skip': 5,
    'waiting_for_skip': '§e{0} §c正在睡觉, §e{1} §c秒后开始跳过夜晚, 点击这条消息取消',
    'already_sleeping': '§c已经有人在睡觉了',
    'no_one_sleeping': '§c没有人在睡觉',
    'not_fall_asleep': '§c您还没有入睡',
    'skip_abort': '§a跳过夜晚已取消',
    'is_daytime': '§c当前为白天'
}


class Single:
    want_skip = False
    commend_sent = False
    now_time = 0
    config = Config('SinglePlayerSleep', default_config)


single = Single()


def on_info(server, info):
    global single
    if single.commend_sent:
        parse_time_info(info.content)


def on_load(server, old):
    global single
    single = Single()
    server.add_help_message('!!sleep', RText(
        '单人睡觉跳过夜晚').c(RAction.run_command, '!!sleep').h('点我跳过夜晚'))


def on_user_info(server, info):
    global single
    if info.content == '!!sleep' and info.is_player:
        if single.want_skip:
            return server.reply(info, single.config['already_sleeping'])
        else:
            want_skip(server, info)
    elif info.content == '!!sleep cancel' and info.is_player:
        if single.want_skip:
            single.want_skip = False
            server.reply(info, single.config['skip_abort'])
        else:
            server.reply(info, single.config['no_one_sleeping'])


def on_unload(server):
    global single
    if single.want_skip:
        server.say(single.config['skip_abort'])
        single.want_skip = False


def want_skip(server, info):
    global single
    get_time(server)
    if single.now_time >= 12542:
        fall_asleep = PlayerAPI.getPlayerInfo(server, info.player, 'SleepTimer')
        if fall_asleep != 100:
            return server.reply(info, single.config['not_fall_asleep'])
    else:
        return server.reply(info, single.config['is_daytime'])
    single.want_skip = True
    need_skip_time = 24000 - single.now_time
    for i in range(1, single.config['wait_before_skip'] + 1):
        if not single.want_skip:
            return
        msg = RText(
            single.config['waiting_for_skip'].format(info.player, i)).c(
            RAction.run_command, '!!sleep cancel'
        )
        server.say(msg)
        time.sleep(1)
    rcon_running = server.is_rcon_running()
    for i in range(0, single.config['skip_wait_time']):
        if not single.want_skip:
            return
        jump_times = int(need_skip_time / single.config['skip_wait_time'])
        if rcon_running:
            server.rcon_query(f'time add {jump_times}')
        else:
            server.execute(f'time add {jump_times}')
        time.sleep(1)
    single.want_skip = False


def get_time(server):
    if server.is_rcon_running():
        parse_time_info(server.rcon_query('time query daytime'))
    else:
        server.execute('time query daytime')
        single.commend_sent = True


def parse_time_info(msg):
    global single
    if re.match(r'The time is .*', msg):
        single.now_time = int(msg.split('is ')[-1])
