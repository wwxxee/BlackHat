import os
import paramiko
import socket
import sys
import threading


# 获取当前运行脚本的绝对路径（不包含文件名）
CWD = os.path.dirname(os.path.realpath(__file__))

HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD, 'test_rsa.key'))


class Server(paramiko.ServerInterface):
    """
    此类定义了一个接口，用于控制 Paramiko 在服务器模式下的行为。
    这个类的方法是从 Paramiko 的主线程调用的.
    参考：https://docs.paramiko.org/en/stable/api/server.html?highlight=ServerInterface
    """
    def __int__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        """
        确定是否将授予给定类型的通道请求，并返回OPEN_SUCCEEDED或返回错误代码。当客户端请求通道时，在身份验证完成后，在服务器模式下调用此方法。
        :param kind:kind ( str ) – 客户端想要打开的频道类型（通常 "session"）。
        :param chanid:该chanid参数是一个小数字，用于唯一标识Transport.
        :return:成功或失败代码
        """
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        """
        确定客户端提供的给定用户名和密码是否可用于身份验证,，默认返回认证失败
        :param username:
        :param password:
        :return:
        """
        if (username == 'andrew' and password == '123.com'):
            return paramiko.AUTH_SUCCESSFUL


if __name__ == '__main__':
    server = '192.168.52.137'
    ssh_port = 2222
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server, ssh_port))
        sock.listen(10)
        print('[+] Listening for connection ...')
        client, addr = sock.accept()
    except Exception as e:
        print('[-] Listen faild: ' + str(e))
        sys.exit(1)
    else:
        print('[+] Got a connection!', client, addr)

    # 在现有套接字或类似套接字的对象上创建新的 SSH 会话
    bhSession = paramiko.Transport(client)
    # 将主机密钥添加到用于服务器模式的密钥列表中。
    bhSession.add_server_key(HOSTKEY)
    server = Server()
    # 开始会话
    bhSession.start_server(server=server)

    # Return the next channel opened by the client over this transport, in server mode超时时间20s,
    chan = bhSession.accept(20)
    if chan is None:
        print("*** No channel.")
        sys.exit(1)

    print("[+] Authenticated!")
    print(chan.recv(1024))
    chan.send('Welcom to bh_ssh')
    try:
        while True:
            command = input("Enter Command: ")
            if command != 'exit':
                chan.send(command)
                r = chan.recv(8192)
                # 如果需要显示中文，将utf8改为gb2312
                print(r.decode('utf8', 'ignore'))
            else:
                chan.send('exit')
                print("exiting")
                bhSession.close()
                break
    except KeyboardInterrupt:
        bhSession.close()




