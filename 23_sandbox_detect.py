from ctypes import byref, c_uint, c_ulong, sizeof, Structure, windll
import random
import sys
import time
import win32api


class LastInputInfo(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_ulong)
    ]


def get_last_input():
    # GetLastInputInfo检索最后一个输入事件的时间,
    # 参数为指向 LASTINPUTINFO 结构的指针，该结构接收最后一个输入事件的时间
    # 它对应的就是上一次系统中检测到输入的时间
    struct_lastinputinfo = LastInputInfo()
    struct_lastinputinfo.cbSize = sizeof(LastInputInfo)
    windll.user32.GetLastInputInfo(byref(struct_lastinputinfo))

    # GetTickCount检索自系统启动以来经过的毫秒数，最长为 49.7 天。
    # 返回值是自系统启动以来经过的毫秒数。
    run_time = windll.kernel32.GetTickCount()

    # 已过时间
    elapsed = run_time - struct_lastinputinfo.dwTime
    print(f"[*] 已经过 {elapsed} 毫秒自最近一次事件")
    return elapsed


class Detector:
    def __init__(self):
        self.double_click = 0
        self.keystrokes = 0
        self.mouse_click = 0

    def get_key_press(self):
        for i in range(0, 0xff):
            # GetAsyncKeyState检查每个按键是否被按下
            state = win32api.GetAsyncKeyState(i)
            if state & 0x001:  # state & 0x001=1为真
                if i == 0x1:  # VK_LBUTTON，0x01	鼠标左键
                    self.mouse_click += 1
                    return time.time()
                elif i > 32 and i < 127:  # 键盘上的ASCII按键
                    self.keystrokes += 1
        return None

    def detect(self):
        previous_timestamp = None
        first_double_click = None
        double_click_threshold = 0.35

        # 存储关于敲击键盘，单机鼠标，双击鼠标三个操作的沙箱检测阈值
        max_double_clicks = 10
        max_keystrokes = random.randint(10, 25)
        max_mouse_clicks = random.randint(5, 25)
        max_input_threshold = 30000  # 30秒

        # 一旦用户输入以来经过的时间大于阈值就退出程序
        last_input = get_last_input()
        if last_input >= max_input_threshold:
            sys.exit(0)

        detection_complete = False

        while not detection_complete:
            keypress_time = self.get_key_press()  # 检查是否发生按键或鼠标事件
            if keypress_time is not None and previous_timestamp is not None:
                # 计算两次鼠标单击的时间差
                elapsed = keypress_time - previous_timestamp

                # 与阈值相比较来判断是否是一次双击事件
                if elapsed <= double_click_threshold:
                    self.mouse_click -= 2
                    self.double_click += 1
                    if first_double_click is None:
                        first_double_click = time.time()
                    else:
                        # 短时间内鼠标双击事件达到最大值就退出
                        if self.double_click >= max_double_clicks:
                            if (keypress_time - first_double_click <=
                                    (max_double_clicks * double_click_threshold)):
                                sys.exit(0)

                # 检测是否通过所有检测
                if (self.keystrokes >= max_keystrokes and self.double_click >= max_double_clicks
                and self.mouse_click >= max_mouse_clicks):
                    detection_complete = True

                previous_timestamp = keypress_time
            elif keypress_time is not None:
                previous_timestamp = keypress_time


if __name__ == '__main__':
    d = Detector()
    d.detect()
    print('okay.')
    # while True:
    #     get_last_input()
    #     time.sleep(1)


