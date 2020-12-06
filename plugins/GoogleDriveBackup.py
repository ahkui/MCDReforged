import os
import time
import shutil
from threading import Lock
from pydrive.auth import GoogleAuth,ServiceAccountCredentials
from pydrive.drive import GoogleDrive
from oauth2client.client import GoogleCredentials

# 可修改變數
Prefix = '!!gdb'
ServerPath = './server'
gdbPath = './plugins/GoogleDriveBackup'
TurnOffAutoSave = True
DeleteLocalFileAfterUpload = True
# 0:guest 1:user 2:helper 3:admin 4:owner
MinimumPermissionLevel = {
    'help':0,
    'make': 1,
    'getAuth': 4,
    'setToken':4,
    'setFolder':4,
}
WorldNames = [
    'world',
]

CredentialsFilePath = os.path.join(gdbPath,'auth_token.json')
DriveAPISecerts = os.path.join(gdbPath,'client_secrets.json')

# 不可修改變數
IgnoreSessionLock = True
plugin_unloaded = False
drive = None
creating_backup = Lock()
def showHelp(server,info):
    print_message(server, info, f'{Prefix} make:建立並上傳備份檔到GoogleDrive')
    print_message(server, info, f'{Prefix} getAuth:獲取GoogleDrive認證網址')
    print_message(server, info, f'{Prefix} setToken <金鑰>:設定GoogleDirve認證碼')
    print_message(server, info, f'{Prefix} setFolder <folderId>:設定上傳的目的資料夾')

def on_load(server, old_module):
    GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = DriveAPISecerts
    GoogleAuth.DEFAULT_SETTINGS['oauth_scope'] = ['https://www.googleapis.com/auth/drive']
    server.add_help_message('!!gdb help', '顯示GoogleDrive備份程式幫助')

def on_unload(server):
    global plugin_unloaded
    plugin_unloaded = True
    
def on_info(server, info):
    if not info.is_user:
        if info.content == 'Saved the game':
            global game_saved
            game_saved = True
        return
    command = info.content.split()
    if len(command) == 0 or command[0] != Prefix:
        return
    cmd_len = len(command)
    
    # MCDR permission check
    global MinimumPermissionLevel
    if cmd_len >= 2 and command[1] in MinimumPermissionLevel.keys():
        if server.get_permission_level(info) < MinimumPermissionLevel[command[1]]:
            print_message(server, info, '§c權限不足！§r')
            return
    
    # !!gdb
    if cmd_len == 1 or (cmd_len >= 2 and command[1]=='help'):
        showHelp(server, info)
    
    # !!gdb make
    elif cmd_len >= 2 and command[1] == 'make':
        create_backup(server, info)
    elif cmd_len >= 2 and command[1] == 'getAuth':
        auth(server,info)
    elif cmd_len >= 3 and command[1] == 'setToken':
        settoken(server,info,command[2])
    elif cmd_len >= 3 and command[1] == 'setFolder':
        setFolderId(server,info,command[2])

def auth(server,info):
    gauth = GoogleAuth(DriveAPISecerts)
    gauth.LoadCredentialsFile(CredentialsFilePath)
    if gauth.credentials is None:
        auth_url = gauth.GetAuthUrl() 
        server.execute('tellraw ' + info.player + ' {"text":"[GDB]: 請前往 §6此網站§r 進行Google Drive取得登入金鑰","underlined":"false","clickEvent":{"action":"open_url","value":"' + auth_url + '"}}')
        print_message(server, info,"並使用!!gdb setToken <金鑰>進行登入設定")
        return None
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile(CredentialsFilePath)
    return gauth

def settoken(server,info,code):
    gauth = GoogleAuth(DriveAPISecerts)
    gauth.LoadCredentialsFile(CredentialsFilePath)
    gauth.Auth(code)
    gauth.SaveCredentialsFile(CredentialsFilePath)
    return gauth
    
def get_drive(server,info):
    global drive
    if drive !=None:
        return drive
    
    gauth = auth(server,info)
    if gauth==None:
        return None
    drive = GoogleDrive(gauth)
    
    return drive

def getFolderId(server,info):
    folderIdPath = f'{gdbPath}/gdFolder.txt'
    if not os.path.exists(folderIdPath):
        print_message(server,info,"請至googleDrive查詢要綁定的資料夾Id(網址列folder/之後的那串亂碼)",tell=False)
        print_message(server,info,"並使用 !!gdb setFolder <folderId>進行綁定",tell=False)
        return None
    with open(folderIdPath) as f:
        folder = f.read()
    return folder

def setFolderId(server,info,folderId):
    folderIdPath = f'{gdbPath}/gdFolder.txt'
    with open(folderIdPath,'w') as f:
        f.write(folderId)
    print_message(server,info,"備份資料夾設定完成!")

def print_message(server, info, msg, tell=True, prefix='[GDB] '):
    msg = prefix + msg
    if info.is_player and not tell:
        server.say(msg)
    else:
        server.reply(info, msg)

def touch_backup_folder():
    def mkdir(path):
        if not os.path.exists(path):
            os.mkdir(path)
    mkdir(gdbPath)

def copy_worlds(src, dst):
    def filter_ignore(path, files):
        return [file for file in files if file == 'session.lock' and IgnoreSessionLock]
    for world in WorldNames:
        shutil.copytree('{}/{}'.format(src, world), '{}/{}'.format(dst, world), ignore=filter_ignore)

def format_time():
    return time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime())

def create_backup(server, info):
    if os.path.exists(f"{gdbPath}/world"):
        shutil.rmtree(f"{gdbPath}/world")
    global creating_backup
    acquired = creating_backup.acquire(blocking=False)
    if not acquired:
        print_message(server, info, '正在§a備份§r中，請不要重複輸入', tell=False)
        return
    try:
        print_message(server, info, '§a備份§r中...請稍等', tell=False)
        start_time = time.time()
        touch_backup_folder()

        # start backup
        global game_saved, plugin_unloaded
        game_saved = False
        if TurnOffAutoSave:
            server.execute('save-off')
        server.execute('save-all')
        while True:
            time.sleep(0.01)
            if game_saved:
                break
            if plugin_unloaded:
                server.reply(info, '插件重載，§a備份§r中斷！', tell=False)
                return

        copy_worlds(ServerPath, gdbPath)
        end_time = time.time()
        print_message(server, info, '§a備份§r完成，耗時§6{}§r秒'.format(round(end_time - start_time, 1)), tell=False)
        
        
        # 壓縮檔案
        print_message(server, info, '§a壓縮備份檔§r中...請稍等', tell=False)
        zip_start_time = time.time()
        bkp_time = format_time()
        shutil.make_archive(f"{gdbPath}/{bkp_time}", 'zip', f"{gdbPath}/world")
        shutil.rmtree(f"{gdbPath}/world")
        zip_end_time = time.time()
        print_message(server, info, '§a壓縮備份檔§r完成，耗時§6{}§r秒'.format(round(zip_end_time - zip_start_time, 1)), tell=False)
        
        # 獲取Google Drive
        drive = get_drive(server,info)
        if drive==None:
            return
        folder = getFolderId(server,info)
        if folder==None:
            return
        # 上傳檔案
        print_message(server, info, f'開始上傳備份檔{bkp_time}.zip', tell=False)
        gd_start_time = time.time()
        file = drive.CreateFile({'parents': [{'id': folder}],'title':f'{bkp_time}.zip'})
        # Read file and set it as a content of this instance.
        file.SetContentFile(f'{gdbPath}/{bkp_time}.zip',)
        file.Upload()
        gd_end_time = time.time()
        print_message(server, info, '上傳§r完成，耗時§6{}§r秒'.format(round(gd_end_time - gd_start_time, 1)), tell=False)
        
        # 解除pydrive object與本機檔案間的連結
        del file
        # 刪除本地檔案
        if DeleteLocalFileAfterUpload:
            os.remove(f'{gdbPath}/{bkp_time}.zip')
    except Exception as e:
        print_message(server, info, '§a備份§r失败，錯誤代碼{}'.format(e), tell=False)
    finally:
        creating_backup.release()
        if TurnOffAutoSave:
            server.execute('save-on')