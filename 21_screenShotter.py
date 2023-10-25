import base64
import win32api
import win32con
import win32gui
import win32ui

"""
https://cloud.tencent.com/developer/article/2153674
pywin32 主要的作用是供 Python开发者快速调用 Windows API的一个模块库。该模块的另一个作用是是通过Python进行COM编程。
win32gui定义了图形操作的API
win32con与上述模块基本一致，这个模块内部定义了Windows API内的宏
Win32 API 即为Microsoft 32位平台的应用程序编程接口
win32com Python 操作 COM 组件的库
"""


def get_dimensions():
    """
    GetSystemMetrics 函数返回主监视器的值.
    :return:
    """
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)  # 虚拟屏幕宽度
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)  # 高度
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)  # 虚拟屏幕左侧坐标
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)  # 虚拟屏幕顶部坐标

    return (width, height, left, top)


def screenshot(name='screenshot'):
    # GetDesktopWindow检索桌面窗口的句柄。
    # 桌面窗口覆盖整个屏幕。 桌面窗口是在上面绘制其他窗口的区域。返回值是桌面窗口的句柄。
    hdesktop = win32gui.GetDesktopWindow()
    width, height, left, top = get_dimensions()

    # GetWindowDC 函数检索整个窗口（包括标题栏、菜单和滚动条） (DC) 的设备上下文
    # 窗口设备上下文允许绘制窗口中的任意位置，因为设备上下文的原点是窗口的左上角，参数是窗口的句柄
    # 如果函数成功，则返回值是指定窗口的设备上下文的句柄
    desktop_dc = win32gui.GetWindowDC(hdesktop)

    # 从一个句柄创建一个上下文（DC对象），返回值是 DC 的句柄
    img_dc = win32ui.CreateDCFromHandle(desktop_dc)

    # CreateCompatibleDC 函数创建与指定设备兼容的内存设备上下文 (DC)
    # 参数为现有DC的句柄，返回值是内存 DC 的句柄
    mem_dc = img_dc.CreateCompatibleDC()

    # CreateBitmap 函数创建具有指定宽度、高度和颜色格式的位图，返回值是位图的句柄
    # 创建位图对象准备保存图片
    screenshot = win32ui.CreateBitmap()

    # CreateCompatibleBitmap 函数创建与设备兼容的位图，该位图与指定的设备上下文相关联
    # 返回值是兼容位图 (DDB) 的句柄
    # 为bitmap开辟存储空间
    screenshot.CreateCompatibleBitmap(img_dc, width, height)

    # SelectObject 函数将对象选择到指定的设备上下文 (DC),位图只能选入内存 DC
    # 选择创建的位图
    mem_dc.SelectObject(screenshot)

    # BitBlt 函数执行与像素矩形相对应的颜色数据的位块传输，从指定的源设备上下文传输到目标设备上下文
    # SRCCOPY 将源矩形直接复制到目标矩形
    # 从桌面图片按位复制并保存到内存设备上下文中
    mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)

    # 保存位图到文件
    screenshot.SaveBitmapFile(mem_dc, f'{name}.bmp')

    # 释放内存
    mem_dc.DeleteDC()
    win32gui.DeleteObject(screenshot.GetHandle())


def run():
    screenshot()
    with open('screenshot.bmp', 'rb') as f:
        img = f.read()

    return img


if __name__ == '__main__':
    screenshot()
