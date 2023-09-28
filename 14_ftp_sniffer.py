from scapy.all import sniff, TCP, IP


def packet_callback(packet):
    if packet[TCP].payload:
        # 从数据包中提取信息payload.original
        mypacket = str(packet[TCP].payload.original, encoding='utf-8')
        if 'USER' in mypacket or 'PASS' in mypacket:
            print(f"[*] Destination: {packet[IP].dst}")
            print(f"[*] {mypacket}")


def main():
    # store=0表示将不会把数据包留在内存里。如果长时间嗅探可设置为0，不会消耗掉过多内存
    sniff(filter='tcp port 21', iface='eth0',prn=packet_callback, store=0)


if __name__ == '__main__':
    main()
