# -*- coding: utf-8 -*-
# v2.3.1

import os
import json
import logging
from copy import deepcopy
from decimal import Decimal


FILE_PATH = './plugins/vault/'


def init_data():
    if not os.path.isfile(FILE_PATH + 'vault.json'):
        with open(FILE_PATH + 'vault.json', 'w') as create:
            create.write(json.dumps({}, indent=1))
    global player_data, str_data
    player_data = {}
    with open(FILE_PATH + 'vault.json') as init:
        str_data = json.load(init)
    for name, balance in str_data.items():
        player_data[name] = Decimal(balance)


def save_data(player, amount):
    str_data[player] = str(amount)
    with open(FILE_PATH + 'vault.json', 'w') as save:
        save.write(json.dumps(str_data, indent=4))
        save.flush()


def add_log(player, action, amount):
    vault_logger.info(player + ' ' + action + ' ' + amount)


def on_load(server, old):
    # 检查文件夹
    if not os.path.exists(FILE_PATH):
        os.makedirs(FILE_PATH)
    # 初始化数据
    init_data()
    # 日志
    global vault_logger, fh
    vault_logger = logging.getLogger('vault_logger')
    vault_logger.setLevel(logging.INFO)
    fh = logging.FileHandler(FILE_PATH + 'vault.log')
    fh.setLevel(logging.INFO)
    fh.setFormatter(
        logging.Formatter('[%(asctime)s] [Vault/%(levelname)s]: %(message)s',
                          datefmt='%Y-%m-%d %H:%M:%S')
    )
    vault_logger.addHandler(fh)


def on_unload(server):
    vault_logger.removeHandler(fh)


def new(player):
    if check(player) == -1:
        player_data[player] = Decimal(0)
        save_data(player, 0)


def pay(player_from, player_to, amount):
    # 检查合法输入
    if amount <= 0:
        return -2
    # 检查账户
    if player_to not in player_data.keys():
        return -1
    # 检查余额
    if check(player_from) >= amount:
        player_data[player_from] -= amount
        player_data[player_to] += amount
        save_data(player_from, player_data[player_from])
        save_data(player_to, player_data[player_to])
        add_log(player_from, '-', str(amount))
        add_log(player_to, '+', str(amount))
        return 1
    else:
        return -3


def top():
    top_data = deepcopy(player_data)
    top_data = sorted(top_data.items(), key=lambda d: d[1], reverse=True)
    return dict(top_data)


def check(player):
    if player in player_data.keys():
        return player_data[player]
    else:
        return -1


def give(player, amount):
    # 检查合法输入
    if amount <= 0:
        return -2
    # 检查账户
    if player not in player_data.keys():
        return -1
    # 保存数据
    player_data[player] += amount
    save_data(player, player_data[player])
    add_log(player, '+', str(amount))
    return 1


def take(player, amount):
    # 检查合法输入
    if amount <= 0:
        return -2
    # 检查余额
    if amount > player_data[player]:
        return -3
    # 检查账户
    if player not in player_data.keys():
        return -1
    # 保存数据
    player_data[player] -= amount
    save_data(player, player_data[player])
    add_log(player, '-', str(amount))
    return 1


def set(player, amount):
    # 检查合法输入
    if amount < 0:
        return -2
    # 检查账户
    if player not in player_data.keys():
        return -1
    # 设置
    player_data[player] = amount
    save_data(player, player_data[player])
    add_log(player, '=', str(amount))
    return 1
