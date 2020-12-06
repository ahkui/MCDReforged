try:
    from urllib import quote
except:
    from urllib.parse import quote

help_msg='''
§r======= §6Minecraft Wiki Searcher §r=======
幫助你更好地查詢Minecraft Wiki~
使用§6!!wiki§r可以叫出本使用方法
使用§6!!wiki [查詢内容]§r可以進行查詢
Minecraft Wiki Searcher Plugin by §6GamerNoTitle
§r======= §6Minecraft Wiki Searcher §r=======
'''

def on_info(server, info):
    if info.content == '!!wiki':
        server.tell(info.player, help_msg)
    else:
        if info.content.startswith('!!wiki') and info.is_player:
            if len(info.content[7:])==0:
                server.tell(info.player, '[wiki]§6參數錯誤！')
            else:
                search_content=info.content[7:]
                server.execute('tellraw ' + info.player + ' {"text":"[wiki]: 查詢 §6' + search_content + '§r 的结果","underlined":"false","clickEvent":{"action":"open_url","value":"https://minecraft-zh.gamepedia.com/index.php?variant=zh-tw&search=' + quote(search_content) + '"}}')
def on_load(server, old_module):
    server.add_help_message('!!wiki', '查詢minecraft wiki')
