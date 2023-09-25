import sys
import socket
import threading


# 提供所有可打印字符,可打印字符的长度为3，不可打印的长度为6，如果不可打印就提供为一个点(.)
HEX_FILTER = ''.join([len(repr(chr(i))) == 3 and chr(i) or '.'for i in range(256)])
"""
HEX_FILTER:
................................ !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[.]^_`abcdefghijklmnopqrstuvwxyz{|}~..................................¡¢£¤¥¦§¨©ª«¬.®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ
"""


def hexdump(src, length=16, show=True):
    """
    接收byte或string类型的输入，并将其转换为16进制格式输出到屏幕上
    这个函数提供了实时观察代理内数据流通的方法
    :param src:
    :param length:
    :param show:
    :return:
    """
    if isinstance(src, bytes):
        src = src.decode()
    result = list()
    for i in range(0, len(src), length):
        word = str(src[i:i+length])
        printable = word.translate(HEX_FILTER)
        # 将word转换为16进制
        hexa = ' '.join([f'{ord(c):02X}' for c in word])
        hexwidth = length*3
        result.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')
    if show:
        for line in result:
            print(line)
    else:
        return result


# hexdump("hello, this is an apple\nhahah\nqq", show=True)


def receive_from(connection):
    """
    接收本地或远程数据
    :param connection: socket对象
    :return: 接收到的数据
    """
    buffer = b""
    connection.settimeout(5)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        pass
    return buffer


def request_handler(buffer):
    # 在代理转发数据包之前，修改一下请求的数据包
    return buffer


def response_handler(buffer):
    # 在代理转发数据包之前，修改一下回复的数据包
    return buffer


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    # 开始之前确认是否需要先从服务器那边接收一段数据
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

    remote_buffer = response_handler(remote_buffer)
    if len(remote_buffer):
        print("[<==] Sending %d bytes to localhost." %len(remote_buffer))
        client_socket.send(remote_buffer)
    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line = "[==>]Received %d bytes from localhost." %len(local_buffer)
            print(line)
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("[<==] Received %d bytes from remote." %len(remote_buffer))
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost.")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print("Problem on bind: %r" % e)
        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions")
        sys.exit(0)

    print("[*] Listening on %s:%d" % (local_host, local_port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        # 打印本地连接信息
        line = "> Received incoming connection from %s:%d" % (addr[0], addr[1])
        print(line)
        # 开启线程去沟通远程连接
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()


def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./tcp_proxy.py [localhost] [localport]", end='')
        print("[remotehost] [remoteport] [receive_first]")
        print("Example: ./tcp_proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)


if __name__ == '__main__':
    main()


# sudo python tcp_proxy.py 192.168.1.203 21 ftp.sun.zc.za 21 True
