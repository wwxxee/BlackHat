# @Function:基于UDP的主机发现工具
import socket
import os


# host to listen on, 本机IP地址
HOST = "10.28.5.179"

def main():
    # create raw socket
    if os.name == 'nt':
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    # windows 允许嗅探任何协议的所有流入数据，Linux需要强制指定一个协议来嗅探
    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    sniffer.bind((HOST, 0))

    # 抓包时包含IP头
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    # 如果在Windows上允许程序，额外发送一条IOCTL消息启用网卡的混杂模式
    # 启动混杂模式后，就能嗅探到流经网卡的所有数据包，包括不归我们接收的数据包
    # 需要管理员权限或root权限
    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    # 接收数据
    print(sniffer.recvfrom(65535))

    # 关闭混杂模式
    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)


if __name__ == '__main__':
    main()
