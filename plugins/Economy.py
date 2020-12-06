# -*- coding: utf-8 -*-
# v3.5.8
VERSION = 'v3.5.8'

import os
import yaml
import time
import logging
import shutil
from decimal import Decimal, ROUND_HALF_UP
from utils.rtext import *

FILE_PATH = 'plugins/Economy/'
DEFAULT_CONFIG = {
    'MAXIMAL_TOPS': 10,
    'DEFAULT_BALANCE': 10.00,
    'REMINDER': True,
    'CMD_PERMISSIONS': {
        'top': 1,
        'check': 2,
        'count': 1,
        'give': 3,
        'take': 3,
        'set': 3,
        'update': 2,
        'reload': 3
        }
    }


HelpMessage = {
'!!money help': '§6!!money help §7查看帮助',
'!!money': '§6!!money §7查询余额',
'!!pay ': '§6!!pay <§6§oplayer§6> <§6§oamount§6> §7将你的钱支付给他人',
'!!money top': '§6!!money top §7查看财富榜',
'!!money check ': '§6!!money check <§6§oplayer§6> §7查询他人余额',
'!!money count ': '§6!!money count <§6§onumber§6> §7计算特定数量玩家总余额，输入all计算所有人',
'!!money give ': '§6!!money give <§6§oplayer§6> <§6§oamount§6> §7给予他人钱',
'!!money take ': '§6!!money take <§6§oplayer§6> <§6§oamount§6> §7拿取他人钱',
'!!money set ': '§6!!money set <§6§oplayer§6> <§6§oamount§6> §7设置他人余额',
'!!money update': '§6!!money update §7更新插件',
'!!money reload': '§6!!money reload §7重载插件'
}

reload_msg = '''§6!!money reload all §7重载所有
§6!!money reload config §7重载配置文件
§6!!money reload data §7重载玩家数据'''


def init_config():
    if not os.path.isfile('./config/economy.yml'):
        with open('./config/economy.yml', 'w') as create:
            create.write(yaml.dump(DEFAULT_CONFIG, indent=4))
    with open('./config/economy.yml') as f:
        config = yaml.safe_load(f)
    global MAXIMAL_TOPS, CMD_PERMISSIONS, DEFAULT_BALANCE, REMINDER
    MAXIMAL_TOPS = config['MAXIMAL_TOPS']
    CMD_PERMISSIONS = config['CMD_PERMISSIONS']
    DEFAULT_BALANCE = config['DEFAULT_BALANCE']
    REMINDER = config['REMINDER']


def make_log_backup():
    year = time.localtime(time.time()).tm_year
    mon = time.localtime(time.time()).tm_mon
    day = time.localtime(time.time()).tm_mday
    old_log_list = os.listdir(FILE_PATH + 'logs/')
    make_backup = False
    if len(old_log_list) > 1:
        old_log_list.sort(reverse=True)
        for old_log_name in old_log_list:
            old_log_name = old_log_name.split('.')[0]
            old_log_name = old_log_name.split('-')
            if len(old_log_name) == 3:
                make_backup = True if int(old_log_name[0]) != year or int(old_log_name[1]) != mon or int(old_log_name[2]) != day else False
    else:
        make_backup = True if len(old_log_list) == 1 and old_log_list[0] == 'Economy.log' else False
    if make_backup:
        shutil.copy(FILE_PATH + 'logs/Economy.log',
                    FILE_PATH + 'logs/{}-{}-{}.log'.format(year, str(mon).zfill(2), str(day).zfill(2)))


def add_log(action, amount=None, user=None, object=None):
    if user is None:
        user = 'console'
    if action == 'reload':
        economy_logger.info('{} reload plugin'.format(user))
    elif action == 'update':
        economy_logger.info('{} update plugin'.format(user))
    elif action == 'load':
        economy_logger.info('loaded Economy')
    elif action == 'new':
        economy_logger.info('{} create account for {} and set balance to {}'.format(user, object, amount))
    elif action.startswith('reload'):
        if action == 'reload_all':
            economy_logger.info('{} reload all'.format(user))
        elif action == 'reload_data':
            economy_logger.info('{} reload data'.format(user))
        elif action == 'reload_config':
            economy_logger.info('{} reload config'.format(user))
    elif action == 'payteam':
        economy_logger.info('{} {} {} to team {}'.format(user, action, amount, object))
    else:
        economy_logger.info('{} {} {} to {}'.format(user, action, amount, object))


def on_load(server, old_module):
    # check folder
    if not os.path.exists(FILE_PATH):
        os.makedirs(FILE_PATH)
    if not os.path.exists(FILE_PATH + 'logs/'):
        os.makedirs(FILE_PATH + 'logs/')
    # vault check
    if 'vault.py' not in server.get_plugin_list():
        server.logger.warning('你没有安装前置vault! ')
    else:
        global vault
        vault = server.get_plugin_instance('vault')
    # add help msg
    server.add_help_message('!!money help', hover_run_command('§a经济系统帮助', '!!money help', '点击查看帮助信息'))
    # team account
    global enable_TeamAccount
    if 'TeamAccount.py' in server.get_plugin_list():
        enable_TeamAccount = True
        global TeamAccount
        TeamAccount = server.get_plugin_instance('TeamAccount')
    else:
        enable_TeamAccount = False
    # init config
    init_config()
    # init log
    global economy_logger, fh
    economy_logger = logging.getLogger('economy_logger')
    economy_logger.setLevel(logging.INFO)
    fh = logging.FileHandler(FILE_PATH + 'logs/Economy.log')
    fh.setLevel(logging.INFO)
    fh.setFormatter(
        logging.Formatter('[%(asctime)s] [Economy/%(levelname)s]: %(message)s',
                          datefmt='%Y-%m-%d %H:%M:%S')
    )
    economy_logger.addHandler(fh)
    add_log('load')

    # make log backup
    make_log_backup()


def on_unload(server):
    enable_TeamAccount = False
    economy_logger.removeHandler(fh)


def on_player_joined(server, player):
    if vault.check(player) == -1:
        vault.new(player)
        vault.set(player, Decimal(DEFAULT_BALANCE).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP))
        add_log('new', DEFAULT_BALANCE, 'server', player)


def on_user_info(server, info):
    # check your self
    if info.content.startswith('!!money'):
        if info.content.rstrip(' ') == '!!money' and info.is_player:
            server.reply(info, '§a您的余额为:§e' + str(vault.check(info.player)))
            return
        content = info.content.rstrip(' ').split(' ')
        if len(content) >= 2:
            permission = server.get_permission_level(info)
            del content[0]
            commands(server, info, content, permission)

    # pay
    if info.content.startswith('!!pay') and info.is_player:
        content = info.content.rstrip(' ').split(' ')
        if len(content) == 3 and content[0] == '!!pay':
            del content[0]
            player_from = info.player
            player_to = content[0]
            amount = round_amount(server, info, content[1])
            if amount is None:
                return wrong_amount(server, info)
            return_info = vault.pay(player_from, player_to, amount)
            if return_info == -1:
                none_account(server, info, player_to)
            elif return_info == -3:
                server.reply(info, '§c余额不足!')
            else:
                add_log('pay', str(amount), player_from, player_to)
                server.reply(info, '§a你向§e' + player_to + '§a支付了§e' + str(amount))
                server.tell(player_to, '§e' + player_from + '§a向你支付了§e' + str(amount))
        elif len(content) == 3 and enable_TeamAccount and content[0] == '!!payteam':
            del content[0]
            amount = round_amount(server, info, content[1])
            if amount is None:
                return wrong_amount(server, info)
            if vault.check(info.player) == -1:
                server.reply(info, '§c余额不足!')
            elif content[0] not in TeamAccount.get_team_list():
                server.reply(info, '§c团队不存在!')
            else:
                add_log('payteam', str(amount), info.player, content[0])
                vault.take(info.player, amount)
                TeamAccount.add_balance(content[0], amount)
                TeamAccount.save_data()
                server.reply(info, '§a你向团队§e' + content[0] + '§a支付了§e' + str(amount))
                team = TeamAccount.get_team_data(content[0])
                for player in team['members']['Management']:
                    server.tell(player, '§e' + info.player + '§a向你的团队支付了§e' + str(amount) + '§a, 团队余额: §e' + team['balance'])
                for player in team['members']['Cashier']:
                    server.tell(player, '§e' + info.player + '§a向你的团队支付了§e' + str(amount) + '§a, 团队余额: §e' + team['balance'])
                for player in team['members']['Member']:
                    server.tell(player, '§e' + info.player + '§a向你的团队支付了§e' + str(amount) + '§a, 团队余额: §e' + team['balance'])


def commands(server, info, content, permission):
    # help
    if content[0] == 'help':
        server.reply(info, '--------Economy 经济插件{}--------'.format(VERSION))
        for cmd, msg in HelpMessage.items():
            server.reply(info, hover_suggest_command(msg, cmd, '点我'))
        if enable_TeamAccount:
            server.reply(info, '§r--------团队账号兼容--------')
            server.reply(info, hover_suggest_command('§6!!payteam <§6§oname§6> <§6§oamount§6> §7将你的钱支付给一个团队', '!!payteam ', '点我'))

    # top
    elif len(content) == 1 and content[0] == 'top':
        if permission < CMD_PERMISSIONS['top']:
            return permission_denied(server, info)
        order = 0
        for name, balance in vault.top().items():
            order += 1
            server.reply(info, '§a' + str(order) + '.§e' + name + '§a - §e' + str(balance))
            if order == MAXIMAL_TOPS:
                break

    # check
    elif len(content) == 2 and content[0] == 'check' and permission >= CMD_PERMISSIONS['check']:
        player = content[1]
        amount = vault.check(player)
        if amount == -1:
            none_account(server, info, player)
        else:
            server.reply(info, '§e' + player + '§a的余额:§e' + str(amount))

    # count
    elif len(content) == 2 and content[0] == 'count':
        if permission < CMD_PERMISSIONS['count']:
            return permission_denied(server, info)
        order = 0
        count = 0
        if content[1] == 'all':
            max_order = 0
        else:
            max_order = int(content[1])
        top_data = vault.top()
        for balance in top_data.values():
            order = order + 1
            count = count + balance
            if order == max_order:
                break
        server.reply(info, '§a总金额为§e' + str(count))

    # give
    elif len(content) == 3 and content[0] == 'give':
        if permission < CMD_PERMISSIONS['give']:
            return permission_denied(server, info)
        player = content[1]
        amount = round_amount(server, info, content[2])
        if amount is None:
            return wrong_amount(server, info)
        if vault.give(player, amount) == -1:
            none_account(server, info, player)
        else:
            add_log('give', str(amount), info.player, player)
            server.reply(info, '§a金钱已给予! §e' + player + '§a现在有§e' + str(vault.check(player)))
            if REMINDER:
                server.tell(player, '§a你被§e给予§a了金钱! 你的余额:§e' + str(vault.check(player)))

    # take
    elif len(content) == 3 and content[0] == 'take':
        if permission < CMD_PERMISSIONS['take']:
            return permission_denied(server, info)
        player = content[1]
        # amount check
        if content[2] == 'all':
            amount = vault.check(player)
        elif Decimal(content[2]) > vault.check(player):
            return server.reply(info, '§c余额不足! 使用!!money take <player> all拿取所有')
        else:
            amount = round_amount(server, info, content[2])
            if amount is None:
                return wrong_amount(server, info)
        if vault.take(player, amount) == -1:
            none_account(server, info, player)
        else:
            add_log('take', str(amount), info.player, player)
            server.reply(info, '§a金钱已拿取! §e' + player + '§a现在有§e' + str(vault.check(player)))
            if REMINDER:
                server.tell(player, '§a你被§e拿取§a了金钱! 你的余额:§e' + str(vault.check(player)))

    # set
    elif len(content) == 3 and content[0] == 'set':
        if permission < CMD_PERMISSIONS['set']:
            return permission_denied(server, info)
        player = content[1]
        amount = round_amount(server, info, content[2], zer=True)
        if amount is None:
            return wrong_amount(server, info)
        if vault.set(player, amount) == -1:
            none_account(server, info, player)
        else:
            add_log('set', str(amount), info.player, player)
            server.reply(info, '§a将§e' + player + '§a的余额设为:§e' + str(amount))
            if REMINDER:
                server.tell(player, '§a你被§e设置§a了金钱! 你的余额:§e' + str(vault.check(player)))

    # update
    elif len(content) == 1 and content[0] == 'update':
        if permission < CMD_PERMISSIONS['update']:
            return permission_denied(server, info)
        if update():
            add_log('update', None, info.player, None)
            server.say('§aEconomy插件已更新')
            server.refresh_changed_plugins()
            server.reply(info, '§a已自动重载插件! ')
        else:
            server.reply(info, '§c更新失败! ')

    # reload
    elif content[0] == 'reload':
        if permission < CMD_PERMISSIONS['reload']:
            return permission_denied(server, info)
        if len(content) == 2 and content[1] == 'all':
            add_log('reload_all', None, info.player, None)
            vault.init_data()
            server.reply(info, '§a已重载配置文件')
            init_config()
            server.reply(info, '§a已重载玩家数据')
        elif len(content) == 2 and content[1] == 'config':
            add_log('reload_config', None, info.player, None)
            init_config()
            server.reply(info, '§a已重载配置文件')
        elif len(content) == 2 and content[1] == 'data':
            add_log('reload_data', None, info.player, None)
            vault.init_data()
            server.reply(info, '§a已重载玩家数据')
        else:
            server.reply(info, reload_msg)

    # wrong command
    else:
        wrong_cmd(server, info)


def wrong_cmd(server, info):
    server.reply(info, '§c命令格式错误! 使用!!money help查看帮助')


def none_account(server, info, player):
    server.reply(info, '§e' + player + '§a没有账户!')


def wrong_amount(server, info):
    server.reply(info, '§c非法金额!')


def permission_denied(server, info):
    server.reply(info, '§c权限不足!')


def hover_suggest_command(message, command, hover):
    return RText(message).c(RAction.suggest_command, command).h(hover)


def run_command(message, command):
    return RText(message).c(RAction.run_command, command)


def hover_run_command(message, command, hover):
    return RText(message).h(hover).c(RAction.run_command, command)


def round_amount(server, info, amount, zer=False):
    if amount.startswith('.') or amount.endswith('.'):
        return None
    elif '.' in amount:
        amount = amount.split('.')
        dec = amount[1]
        dec = dec.ljust(2, '0')[:2]
        if not amount[0].isdigit() or not dec.isdigit():
            return None
        else:
            amount = Decimal('.'.join((amount[0], dec)))
            if amount == 0:
                if zer:
                    return amount
                else:
                    return None
            else:
                return amount
    elif amount.isdigit():
        amount = Decimal(amount)
        if amount == 0:
            if zer:
                return amount
            else:
                return None
        else:
            return amount
    else:
        return None


def update():
    try:
        from requests import get
        file = get('https://raw.githubusercontent.com/zhang-anzhi/Economy/master/Economy.py')
        with open('./plugins/Economy.py', "wb") as f:
            f.write(file.content)
            return True
    except:
        return False
