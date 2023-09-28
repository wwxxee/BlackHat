from scapy.all import sniff, TCP, IP


def packet_callback(packet):
    if packet[TCP].payload:
        mypacket = str(packet[TCP].payload)
        if 'user' in mypacket.lower() or 'pass' in mypacket.lower():
            print(f"[*] Destination: {packet[IP].dst}")
            print(f"[*] {str(packet[TCP].payload)}")


def main():
    # store=0表示将不会把数据包留在内存里。如果长时间嗅探可设置为0，不会消耗掉过多内存
    sniff(filter='tcp port 110 or tcp port 25 or tcp port 143', prn=packet_callback, store=0)


if __name__ == '__main__':
    print("go to do sniff")
    main()
