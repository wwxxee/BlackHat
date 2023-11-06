import os
import sys
import win32api
import win32con
import win32security  # win32 安全API的接口
import wmi


"""
wmi的python参考：http://timgolden.me.uk/python/wmi/tutorial.html
"""


def get_process_privileges(pid):
    try:
        # wincon内定义windows API 内的宏（常量）
        # https://learn.microsoft.com/zh-cn/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocess
        # PROCESS_QUERY_INFORMATION检索有关进程的某些信息（例如其令牌、退出代码和优先级类
        # 返回值是指定进程的打开句柄
        hproc = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)

        # OKEN_QUERY查询访问令牌所必需的
        # 如果该函数成功，则返回值为非零值。
        htok = win32security.OpenProcessToken(hproc, win32con.TOKEN_QUERY)

        # GetTokenInformation 函数检索有关访问令牌的指定类型的信息
        # TOKEN_PRIVILEGES 包含令牌特权的结构,该值标识函数检索的信息的类型。
        # 返回 PyTOKEN_PRIVILEGES （每个权限的 LUID 和属性标志的元组）
        privs = win32security.GetTokenInformation(htok, win32security.TokenPrivileges)

        privileges = ''
        for priv_id, flags in privs:
            if flags == (win32security.SE_PRIVILEGE_ENABLED |
                        win32security.SE_PRIVILEGE_ENABLED_BY_DEFAULT):
                # LookupPrivilegeName返回特权LUID的文本名称
                # 本地唯一标识符(LUID) 一个 64 位值，在系统重启之前保证在生成它的操作系统上是唯一的。
                # 该处查询系统上所拥有的特权常量名称
                privileges += f'{win32security.LookupPrivilegeName(None, priv_id)}|'
    except Exception:
        privileges = 'N/A'

    return privileges


def log_to_file(message):
    with open('process_monitor_log.csv', 'a') as fd:
        fd.write(f'{message}\r\n')


def monitor():
    head = 'CommandLine, Time, Executable, Parent PID, PID, User, Privileges'
    log_to_file(head)
    # 实例化WMI类
    c = wmi.WMI()
    # 监控进程创建事件
    process_watcher = c.Win32_Process.watch_for("creation")
    while True:
        try:
            # https://learn.microsoft.com/zh-cn/windows/win32/cimwin32prov/win32-process
            # https://qiita.com/kanatatsu64/items/4082ba66104b4909eb13

            # 轮询等待返回一个新的进程事件，这个事件是Win32_Process类
            new_process = process_watcher()
            cmdline = new_process.CommandLine
            create_date = new_process.CreationDate
            executable = new_process.ExecutablePath
            parent_id = new_process.ParentProcessId
            pid = new_process.ProcessId
            proc_owner = new_process.GetOwner()

            privileges = get_process_privileges(pid)
            process_log_message = (
                f'{cmdline}, {create_date}, {executable}, '
                f'{parent_id}, {pid}, {proc_owner}, {privileges}'
            )
            print(process_log_message)
            print()
            log_to_file(process_log_message)
        except Exception:
            pass


if __name__ == '__main__':
    monitor()


