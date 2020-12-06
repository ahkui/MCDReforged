# -*- coding: utf-8 -*-

def on_load(server, old_module):
    server.add_help_message('!!seed', '查看地圖種子')

def on_info(server, info):
    if info.is_player and info.content == '!!seed':
        global playername
        playername = info.player
        server.execute('/seed')
    if info.content.startswith('Seed: ['):
        seed = info.content.split('[')[1].split(']')[0]
        server.execute('/tellraw '+playername+' [{"text":"Seed:[","bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false},{"text":"'+seed+'","color":"green","bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"insertion":"'+seed+'","clickEvent":{"action":"suggest_command","value":"'+seed+'"},"hoverEvent":{"action":"show_text","value":"點擊複製到聊天欄"}},{"text":"]","bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false}]')