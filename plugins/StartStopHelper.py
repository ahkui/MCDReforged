# -*- coding: utf-8 -*-

import time


def wait(server, command, time_wait):
    while time_wait > 0:
        if server.is_server_startup():
            server.say('§cServer will {} in {}s§r'.format(command, time_wait))
        time.sleep(1)
        time_wait -= 1


CMD_PREFIX = '!!server'
RECOGNIZED_CMDS = [
    'start',
    'stop',
    'stop_exit',
    'restart'
]

def on_load(server, old_module):
    server.add_help_message(f"{CMD_PREFIX} [{'|'.join(RECOGNIZED_CMDS)}]", '伺服器操作開啟/停止/停止並退出/重啟')

def on_info(server, info):
    if info.is_user:
        args = info.content.split(' ')
        if len(args) not in [1, 2] or not args[0].startswith(CMD_PREFIX):
            return

        command = args[0][len(CMD_PREFIX):]
        if command not in RECOGNIZED_CMDS:
            return

        if server.get_permission_level(info) >= 3:  # admin
            if len(args) == 2 and not args[1].isdigit():
                server.reply(info, '[<time_wait>] argument need to be a number')
                return
            time_wait = int(args[1]) if len(args) == 2 else 10
            if command == 'start':
                server.start()
            elif command == 'stop':
                wait(server, 'stop', time_wait)
                server.stop()
            elif command == 'stop_exit':
                wait(server, 'stop', time_wait)
                server.stop_exit()
            elif command == 'restart':
                wait(server, 'restart', time_wait)
                server.restart()
        else:
            server.reply(info, '§cPermission denied§r')
