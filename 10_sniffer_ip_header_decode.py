# @Function:基于UDP的主机发现工具，解码IP层

import socket
import os
import ipaddress
import struct
import sys


class IP:

    def __init__(self, buff=None):
        header = struct.unpack('<BBHHHBBH4s4s', buff)
        self.ver = header[0] >> 4           # 版本
        self.ihl = header[0] & 0xf          # 头长度
        self.tos = header[1]                # 服务类型
        self.len = header[2]                # 总长度
        self.id = header[3]                 # 标识
        self.offset = header[4]             # 偏移
        self.ttl = header[5]                # ttl（生存时间）
        self.protocol_num = header[6]       # 协议号
        self.sum = header[7]                # 头检验和
        self.src = header[8]                # 源IP地址
        self.dst = header[9]                # 目的IP地址

        self.src_address = ipaddress.ip_address(self.src)
        self.dst_address = ipaddress.ip_address(self.dst)

        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except Exception as e:
            print('%s No protocol matched for %s' % (e, self.protocol_num))
            self.protocol = str(self.protocol_num)


def sniff(host):
    # create raw socket
    if os.name == 'nt':
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    # windows 允许嗅探任何协议的所有流入数据，Linux需要强制指定一个协议来嗅探
    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    sniffer.bind((host, 0))

    # 抓包时包含IP头
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    # 如果在Windows上允许程序，额外发送一条IOCTL消息启用网卡的混杂模式
    # 启动混杂模式后，就能嗅探到流经网卡的所有数据包，包括不归我们接收的数据包
    # 需要管理员权限或root权限
    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    try:
        while True:
            # 读取一个数据包
            raw_buffer = sniffer.recvfrom(65535)[0]
            # 将前20个字节转换成IP头对象
            ip_header = IP(buff=raw_buffer[0:20])

            print('Protocol: %s %s -> %s' %(ip_header.protocol, ip_header.src_address, ip_header.dst_address))

    except KeyboardInterrupt:
        # 如果在windows中，关闭混杂模式
        if os.name == 'nt':
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
        sys.exit()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        host = '192.168.114.26'
    sniff(host)
