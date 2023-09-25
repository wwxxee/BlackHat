# @Function:基于UDP的主机发现工具，扫描器

import socket
import os
import ipaddress
import struct
import sys
import time
import threading


SUBNET = '10.28.5.0/24'
# magic string
MESSAGE = "PYTHONRULES!"


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


class ICMP:
    def __init__(self, buff):
        header = struct.unpack('<BBHHH', buff)
        self.type = header[0]       # 类型
        self.code = header[1]       # 代码
        self.sum = header[2]        # 校验和
        self.id = header[3]         # 标识
        self.seq = header[4]        # 序列号


class Scanner:
    def __init__(self, host):
        self.host = host
        if os.name == 'nt':
            socket_protocol = socket.IPPROTO_IP
        else:
            socket_protocol = socket.IPPROTO_ICMP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
        self.socket.bind((host, 0))
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        if os.name == 'nt':
            self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    def sniffer(self):
        hosts_up = set([f'{str(self.host)} *'])
        try:
            while True:
                # 读取一个数据包
                raw_buffer = self.socket.recvfrom(65535)[0]
                ip_header = IP(buff=raw_buffer[0:20])
                if ip_header.protocol == "ICMP":
                    # IP包头长度为20-60个字节，普通IP报文（不包含可选项）的ihl字段值为5，即20个字节
                    offset = ip_header.ihl * 4
                    buf = raw_buffer[offset:offset + 8]
                    icmp_header = ICMP(buf)
                    if icmp_header.code == 3 and icmp_header.type == 3:
                        # 当一台主机发送出ICMP消息时，会把触发ICMP消息的原始数据包的IP头附在消息末尾
                        if ipaddress.ip_address(ip_header.src_address) in ipaddress.IPv4Network(SUBNET):
                            if raw_buffer[len(raw_buffer) - len(MESSAGE):] == bytes(MESSAGE, 'utf8'):
                                tgt = str(ip_header.src_address)
                                if tgt != self.host and tgt not in hosts_up:
                                    hosts_up.add(str(ip_header.src_address))
                                    print(f'Host Up: {tgt}')
        except KeyboardInterrupt:
            if os.name == 'nt':
                self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

            print('\nUser Interrupted.')
            if hosts_up:
                print(f'\nSummary: Hosts up on {SUBNET}')
            for host in sorted(hosts_up):
                print(f'{host}')
            print('')
            sys.exit()


def udp_sender():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
        for ip in ipaddress.ip_network(SUBNET).hosts():
            sender.sendto(bytes(MESSAGE, 'utf8'), (str(ip), 65212))


if __name__ == '__main__':
    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        host = '192.168.114.26'
    s = Scanner(host)
    time.sleep(1)
    t = threading.Thread(target=udp_sender())
    t.start()
    s.sniffer()
