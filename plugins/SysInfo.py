import psutil
import platform


def get_proc_by_id(pid):
    return psutil.Process(pid)


def get_proc_by_name(pname):
    """ get process by name

    return the first process if there are more than one
    """
    for proc in psutil.process_iter():
        try:
            if proc.name() == pname:
                return proc  # return if found one
        except psutil.AccessDenied:
            pass
        except psutil.NoSuchProcess:
            pass
    return None


def ps(text):
    return round((text/1024/1024), 2)


def send_message(server, player, tell):
    system_info = platform.architecture()
    cpu_count = psutil.cpu_count()
    using_cpu = psutil.cpu_percent(1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    proc = get_proc_by_name("java")
    java_cpu = psutil.Process(proc.pid).cpu_percent(1)
    java_mem = proc.memory_info().rss / psutil.virtual_memory().total * 100
    java_mem = round(java_mem, 2)
    output = """=============== 计算机信息 ===============
注意，以下內容可能不準確，僅供參考。

電腦系統：§b{}
CPU個數:§b{}§r  總CPU佔用:§b{}%
總記憶體佔用：§b{}%§r (§b{}MB§r/§b{}MB§r)
磁片佔用:§b{}%§r (§b{}MB§r/§b{}MB§r)

其中，JAVA 佔用CPU:§b{}%§r，佔用記憶體:§b{}%
=======================================""".format(system_info, cpu_count, using_cpu, mem.percent, ps(mem.used), ps(mem.total), 100-disk.percent, ps(disk.free), ps(disk.total), java_cpu, java_mem)
    for line in output.splitlines():
        if tell:
            server.tell(player, '[SYS] ' + line)
        else:
            print('[SYS] ' + line)


def on_info(server, info):
    if info.is_player and info.content == '!!sysinfo':
        server.tell(info.player, '[SYS]§a請稍後，正在獲取中...')
        send_message(server, info.player, True)
    elif info.content == '!!sysinfo':
        print('[SYS]請稍後，正在獲取中...')
        send_message(server, info.player, False)


def on_load(server, old_module):
    server.add_help_message(f"!!sysinfo", '顯示伺服器資訊')
