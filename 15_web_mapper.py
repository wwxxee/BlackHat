"""
打印wordpress系统结构
@author：
先下载开源的wordpress结构，获得其目录结构，再扫描在线目标。
"""
import contextlib
import os
import queue
import requests
import sys
import threading
import time


FILE_FILTER = [".jpg", ".gif", ".png", ".css"]
TARGET = "http://69.235.149.104"
THREAD = 10

answers = queue.Queue()  # 先进先出队列，不设置长度默认为无限长
web_paths = queue.Queue()


def gather_paths():
    # os.walk() 方法是一个简单易用的文件、目录遍历器
    # root是指当前正在遍历的这个目录本身的地址
    # dirs是一个list，内容是目录中所有的目录的名字（不包含子目录）
    # files是一个list，内容是该目录中的所有文件（不包含子目录）
    for root, dirs, files in os.walk("."):
        for fname in files:
            # splitext分离文件名与扩展名,返回（name, extension）元组
            if os.path.splitext(fname)[1] in FILE_FILTER:
                continue
            path = os.path.join(root, fname)
            if path.startswith('.'):
                path = path[1:]
                if os.name == 'nt':
                    path = path.replace("\\", "/")

            print(path)
            web_paths.put(path)


# contextlib 是一个装饰器，只要按照它的代码协议来实现函数内容，就可以将这个函数对象变成一个上下文管理器
@contextlib.contextmanager
def chdir(path):
    """
    enter: 进入指定目录
    exit: 退出到原始目录
    :param path:
    :return:
    """
    this_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(this_dir)


def test_remote():
    while not web_paths.empty():
        path = web_paths.get()
        url = f'{TARGET}{path}'
        time.sleep(2)
        r = requests.get(url)
        if r.status_code == 200:
            answers.put(url)
            sys.stdout.write("+")
        else:
            sys.stdout.write("x")
        sys.stdout.flush()


def run():
    mythreads = list()
    for i in range(THREAD):
        print(f'Spawning thread {i}')
        t = threading.Thread(target=test_remote)
        mythreads.append(t)
        t.start()

    for thread in mythreads:
        thread.join()  # join使得子线程先结束后再结束主线程


if __name__ == '__main__':
    with chdir("C:\\Users\\xxx\\Downloads\\wordpress-6.0.5\\wordpress"):
        gather_paths()
    input("Press return to continue.")

    run()
    with open('15_web_myanswers.txt', 'w') as f:
        while not answers.empty():
            f.write(f'{answers.get()} \n')
    print('Done!')
