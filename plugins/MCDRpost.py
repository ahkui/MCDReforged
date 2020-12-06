# -*- coding: utf-8 -*-

import json
import time
import os
import shutil

from utils.rtext import *

Prefix = '!!po'
maxStorageNum = 5   # 最大存储訂單量，设为-1则无限制
saveDelay = 1
orders = {
    'players': [],
    'ids': [0]
}
OrderJsonDirectory = './plugins/MCDRpost/'
OrderJsonFile = OrderJsonDirectory + 'PostOrders.json'


def getHelpMessage(server, info):
    msgs_on_helper = RText('')
    msgs_on_admin = RText('')
    if server.get_permission_level(info) > 1:
        # helper以上权限的添加信息
        msgs_on_helper = RTextList(
            RText(Prefix+' ls orders', RColor.gray).c(RAction.suggest_command,
                                                      "!!po ls orders").h('點擊寫入聊天室'), RText(' | 查看現在中轉站內所有包裹\n')
        )
    if server.get_permission_level(info) > 2:
        # admin以上权限的添加信息
        msgs_on_admin = RTextList(
            RText(Prefix+' player add §e[<玩家id>]', RColor.gray).c(
                RAction.suggest_command, "!!po player add ").h('點擊寫入聊天室'), RText(' | 手動註冊玩家到可寄送玩家列表\n'),
            RText(Prefix+' player remove §e[<玩家id>]', RColor.gray).c(
                RAction.suggest_command, "!!po player remove ").h('點擊寫入聊天室'), RText(' | 刪除某註冊的玩家\n'),
        )
    return RTextList(
        RText('--------- §3MCDRpost §r---------\n'),
        RText('一个用於郵寄/傳送物品的MCDR插件\n'),
        RText('§a『命令說明』§r\n'),
        RText(Prefix, RColor.gray).c(RAction.suggest_command,
                                     "!!po").h('點擊寫入聊天室'), RText('  | 顯示幫助信息\n'),
        RText(Prefix+' p §e[<收件人id>] §b[<備註>]', RColor.gray).c(RAction.suggest_command,
                                                               "!!po p ").h('點擊寫入聊天室'), RText(' | 將副手物品發送给§e[收件人]§r。§b[備註]§r为可選項\n'),
        RText(Prefix+' rl', RColor.gray).c(RAction.suggest_command,
                                           "!!po rl").h('點擊寫入聊天室'), RText(' | 列出收件列表\n'),
        RText(Prefix+' r §6[<包裹編號>]', RColor.gray).c(RAction.suggest_command,
                                                     "!!po r ").h('點擊寫入聊天室'), RText(' | 確認收取該包裹編號的物品到副手(收取前將副手清空)\n'),
        RText(Prefix+' pl', RColor.gray).c(RAction.suggest_command,
                                           "!!po pl").h('點擊寫入聊天室'), RText(' | 列出送件列表\n'),
        RText(Prefix+' c §6[<包裹編號>]', RColor.gray).c(RAction.suggest_command, "!!po c ").h(
            '點擊寫入聊天室'), RText(' | 取消傳送物品(收件人未收件前)，該包裹編號物品退回到副手(取消前請將副手清空)\n'),
        RText(Prefix+' ls players', RColor.gray).c(RAction.suggest_command,
                                                   "!!po ls players").h('點擊寫入聊天室'), RText(' | 查看可被寄送的註冊玩家列表\n'),
        msgs_on_helper,
        msgs_on_admin,
        RText('-----------------------')
    )


def getNextId():
    nextid = 1
    orders['ids'].sort()
    for i, id in enumerate(orders['ids']):
        if i != id:
            nextid = i
            orders['ids'].append(nextid)
            return str(nextid)
    nextid = len(orders['ids'])
    orders['ids'].append(nextid)
    return str(nextid)


def loadOrdersJson(server):
    global orders
    if not os.path.isfile(OrderJsonFile):
        server.logger.info('[MCDRpost] 未找到資料檔案，自動生成')
        os.makedirs(OrderJsonDirectory)
        with open(OrderJsonFile, 'w+') as f:
            f.write('{"players": [], "ids":[]}')
    if os.path.exists('./plugins/PostOrders.json'):
        # v0.1.1的插件資料文件位置移动
        shutil.move('./plugins/PostOrders.json', OrderJsonFile)
    try:
        with open(OrderJsonFile) as f:
            orders = json.load(f, encoding='utf8')
    except:
        return


def saveOrdersJson():
    global orders
    try:
        with open(OrderJsonFile, 'w+') as f:
            json.dump(orders, f, indent=4)
        server.logger.info("[MCDRpost] Saved OrderJsonFile")
    except:
        return


def regularSaveOrderJson():
    if len(orders['ids']) % saveDelay == 0:
        saveOrdersJson()


def format_time():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())


def checkPlayer(player):
    for id in orders['players']:
        if id == player:
            return True
    return False


def checkStorage(player):
    num = 0
    if maxStorageNum < 0:
        return True
    for orderid in orders['ids']:
        try:
            order = orders[str(orderid)]
        except:
            continue
        if order.get('sender') == player:
            num += 1
            if num >= maxStorageNum:
                return False
    return True


def checkOrderOnPlayerJoin(player):
    for orderid in orders['ids']:
        try:
            order = orders[str(orderid)]
        except:
            continue
        if order.get('receiver') == player:
            return True
    return False


def getOffhandItem(server, player):
    PlayerInfoAPI = server.get_plugin_instance('PlayerInfoAPI')
    try:
        offhandItem = PlayerInfoAPI.getPlayerInfo(
            server, player, 'Inventory[{Slot:-106b}]', 3)
        if type(offhandItem) == dict:
            return offhandItem
        else:
            return None
    except:
        return None


def delOrder(server, id):
    global orders
    try:
        orders.pop(id)
        orders['ids'].remove(int(id))
    except Exception:
        server.logger.info("Error occurred during delete one PostOrder")
        return False


def getItem(server, player, orderid):
    if not getOffhandItem(server, player):
        order = orders.get(orderid, -1)

        # Vanilla Parser
        server.execute('replaceitem entity ' + player +
                       ' weapon.offhand ' + str(order['item']))

        # Paper Parser
        # server.execute('item entity ' + player +
        #                ' weapon.offhand replace ' + str(order['item']))

        server.execute('execute at ' + player +
                       ' run playsound minecraft:entity.bat.takeoff player ' + player)
        delOrder(server, orderid)
        return True
    else:
        server.tell(player, '§e* 抱歉，請先將您的§6副手物品§e清空')
        return False


def postItem(server, info):
    # !!po receiver infomsg
    sender = info.player
    itemjson = getOffhandItem(server, sender)
    infomsg = "无備註信息"
    postId = None
    if not checkStorage(sender):
        server.tell(sender, '§e* 您現在存放在中轉站的包果數量已達到了上限:' +
                    str(maxStorageNum)+'\n命令 §7!!po pl §e查看您在中轉站内的發送訂單')
        return
    if len(info.content.split()) >= 3:
        receiver = info.content.split()[2]
    else:
        server.tell(sender, '§e* 您的輸入有誤，命令 §7!!po §e可查看幫助信息')
        return
    if len(info.content.split()) >= 4:
        infomsg = info.content.split()[3]
    if not checkPlayer(receiver):
        server.tell(sender, '§e* 收件人 §b'+receiver +
                    ' §e未曾進服，不在登记玩家内，不可被發送，請檢查您的輸入')
        return
    if sender == receiver:
        server.tell(sender, '§e* 寄件人和收件人不能是同一人~')
        return
    if not itemjson:
        server.tell(sender, '§e* 副手檢測不到可寄送的物品，請檢查副手')
        return
    else:
        item = str(itemjson.get('id')) + str(itemjson.get('tag', '')
                                             ) + ' ' + str(itemjson.get('Count', ''))
        postId = getNextId()
        orders[postId] = {
            'time': format_time(),
            'sender': sender,
            'receiver': receiver,
            'item': item,
            'info': infomsg
        }

        # Vanilla Parser
        server.execute('replaceitem entity '+sender +
                       ' weapon.offhand minecraft:air')

        # Paper Parser
        # server.execute('item entity '+sender +
        #                ' weapon.offhand replace minecraft:air')

        server.tell(
            sender, '§6* 物品存放於中轉站，等待對方接收\n* 使用 §7!!po pl §6可以查看還未被查收的發送列表')
        server.execute('execute at ' + sender +
                       ' run playsound minecraft:entity.arrow.hit_player player ' + sender)
        server.tell(
            receiver, '§6[MCDRpost] §e您有一件新包裹，命令 §7!!po rl §e查看收件箱\n* 命令 §7!!po r '+postId+' §e直接收取該包裹')
        server.execute('execute at ' + receiver +
                       ' run playsound minecraft:entity.arrow.shoot player ' + receiver)
        regularSaveOrderJson()


def cancelOrder(server, info):
    # !!po c orderid
    player = info.player
    orderid = None
    if len(info.content.split()) >= 3:
        orderid = info.content.split()[2]
    else:
        server.tell(player, '§e* 未輸入需要取消的包裹編號，§7!!po §e可查看幫助信息')
        return False
    try:
        if not player == orders[orderid]['sender']:
            server.tell(player, '§e* 該訂單非您寄送，您無權對其操作，請檢查輸入')
            return False
    except KeyError:
        server.tell(player, '§e* 未查詢到該包裹編號，檢查輸入')
        return False
    if not getItem(server, player, orderid):
        return False
    server.tell(player, '§e* 已成功取消包裹 '+orderid+'，物品回收至副手')
    regularSaveOrderJson()


def receiveItem(server, info):
    # !!po c orderid
    player = info.player
    orderid = None
    if len(info.content.split()) >= 3:
        orderid = info.content.split()[2]
    else:
        server.tell(player, '§e* 未輸入需要取消的包裹編號，§7!!po §e可查看幫助')
        return False
    try:
        if not player == orders[orderid]['receiver']:
            server.tell(player, '§e* 您非該包裹收件人，無權對其操作，請檢查輸入')
            return False
    except KeyError:
        server.tell(player, '§e* 未查詢到包裹編號，請檢查輸入')
        return False
    if not getItem(server, player, orderid):
        return False
    server.tell(player, '§e* 已成功收取包裹 '+orderid+'，物品接收至副手')
    regularSaveOrderJson()


def listOutbox(server, info):
    listmsg = ''
    for orderid in orders['ids']:
        order = orders.get(str(orderid))
        if not order:
            continue
        if order.get('sender') == info.player:
            listmsg = listmsg+f"{orderid:^8}  |{order.get('sender'):^12}|{order.get('receiver'):^12}| "+order.get(
                'time')+'  | '+order.get('info')+'\n    '
    if listmsg == '':
        server.tell(info.player, '§6* 您現在沒有包裹訂單在中轉站~')
        return
    listmsg = '''==========================================
 包裹編號    |   寄件人  |   收件人  |      發送時間     |   備註
    {0}
    -------------------------------------------
    §6使用命令 §7!!po c [包裹編號] §6取消包裹§r
==========================================='''.format(listmsg)
    server.tell(info.player, listmsg)


def listInbox(server, info):
    listmsg = ''
    for orderid in orders['ids']:
        order = orders.get(str(orderid))
        if not order:
            continue
        if order.get('receiver') == info.player:
            listmsg = listmsg+f"{orderid:^8}  |{order.get('sender'):^12}|{order.get('receiver'):^12}| "+order.get(
                'time')+'  | '+order.get('info')+'\n    '
    if listmsg == '':
        server.tell(info.player, '§e* 您現在沒有待收包裹~')
        return
    listmsg = '''==========================================
 包裹編號    |   寄件人  |   收件人  |      發送時間     |   備註
    {0}
    -------------------------------------------
    §6使用命令 §7!!po r [包裹編號] §6來接收包裹§r
==========================================='''.format(listmsg)
    server.tell(info.player, listmsg)


def listOrders(server, info):
    # !!po ls orders
    listmsg = ''
    if server.get_permission_level(info) < 2:
        listmsg = '§c* 抱歉，您没有權限使用該命令'
    else:
        for orderid in orders['ids']:
            order = orders.get(str(orderid))
            if not order:
                continue
            listmsg = listmsg+f"{orderid:^8}  |{order.get('sender'):^12}|{order.get('receiver'):^12}| "+order.get(
                'time')+'  | '+order.get('info')+'\n    '
        if listmsg == '':
            server.reply(info, '§6* 中轉站内沒有任何包裹~')
            return
        listmsg = '''==========================================
 包裹編號    |   寄件人  |   收件人  |      發送時間     |   備註
    {0}
==========================================='''.format(listmsg)
    server.reply(info, listmsg)


def listPlayers(server, info):
    # !!po ls players
    if server.get_permission_level(info) < 1:
        server.tell(info.player, '§c* 抱歉，您没有權限使用該命令')
        return
    server.reply(info, '§6[MCDRpost] §e可寄送的註冊玩家列表：\n§r' +
                 str(orders.get('players')))


def removePlayerInList(server, info):
    global orders
    playerId = ''
    if server.get_permission_level(info) < 3:
        server.tell(info.player, '§c* 抱歉，您没有權限使用該命令')
        return
    if len(info.content.split()) == 4:
        playerId = info.content.split()[3]
    else:
        server.tell(info.player, '§4* 玩家id格式有誤，請檢查後再輸入')
        return False

    if orders.get('players').count(playerId) == 0:
        server.tell(
            info.player, '§4* 該玩家未註冊，無法進行刪除 \n§r使用 §7!!po ls players §r可以查看所有註冊玩家列表')
        return
    orders.get('players').remove(playerId)
    server.tell(info.player, '§e[MCDRpost] §a成功刪除玩家 §b' +
                playerId+' §a,使用 §7!!po ls players §a可以查看所有註冊玩家列表')
    server.logger.info('[MCDRpost] 已刪除登記玩家 '+playerId)
    saveOrdersJson()


def addPlayerToList(server, info):
    global orders
    playerId = ''
    if server.get_permission_level(info) < 3:
        server.tell(info.player, '§c* 抱歉，您沒有權限使用該命令')
        return
    if len(info.content.split()) == 4:
        playerId = info.content.split()[3]
    else:
        server.tell(info.player, '§4* 玩家id格式有誤，請檢查後再輸入')
        return False

    if orders.get('players').count(playerId) != 0:
        server.tell(
            info.player, '§4* 該玩家已註冊，請檢查後再輸入 \n§r使用 §7!!po ls players §r可以查看所有註冊玩家列表')
        return
    orders.get('players').append(playerId)
    server.tell(info.player, '§e[MCDRpost] §a成功註冊玩家 §b' +
                playerId+' §a,使用 §7!!po ls players §a可以查看所有註冊玩家列表')
    server.logger.info('[MCDRpost] 已登記玩家 '+playerId)
    saveOrdersJson()


def on_info(server, info):
    if info.is_user:
        if info.content == Prefix:
            server.reply(info, getHelpMessage(server, info))
        elif info.content.startswith(Prefix+' p '):
            postItem(server, info)
        elif info.content == Prefix+' pl':
            listOutbox(server, info)
        elif info.content.startswith(Prefix+' r '):
            receiveItem(server, info)
        elif info.content == Prefix+' rl':
            listInbox(server, info)
        elif info.content.startswith(Prefix+' c '):
            cancelOrder(server, info)
        elif info.content == Prefix+' ls orders':
            listOrders(server, info)
        elif info.content == Prefix+' ls players':
            listPlayers(server, info)
        elif info.content.startswith(Prefix+' player add '):
            addPlayerToList(server, info)
        elif info.content.startswith(Prefix+' player remove '):
            removePlayerInList(server, info)


def on_load(server, old_module):
    loadOrdersJson(server)
    server.add_help_message(Prefix, "傳送/接收副手物品")


def on_server_startup(server):
    loadOrdersJson(server)


def on_player_joined(server, player):
    global orders
    flag = True
    for id in orders['players']:
        if id == player:
            flag = False
            if checkOrderOnPlayerJoin(player):
                time.sleep(3)   # 延迟 3s 后再提示，防止更多進服消息混杂而看不到提示
                server.tell(
                    player, "§6[MCDRpost] §e您有待查收的包裹~ 命令 §7!!po rl §e查看詳情")
                server.execute(
                    'execute at ' + player + ' run playsound minecraft:entity.arrow.hit_player player ' + player)
    if flag:
        orders['players'].append(player)
        server.logger.info('[MCDRpost] 已登記玩家 '+player)
        saveOrdersJson()
