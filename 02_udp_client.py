import socket

target_host = "127.0.0.1"
target_port = 9998

# create socket object
# AF_INET参数表示使用标准的IPv4地址或主机名，SOCK_STREAM表示TCP连接
# SOCK_DGRAM表示UDP连接
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# send data
client.sendto(b"hello,go", (target_host, target_port))

# receive data
data, addr = client.recvfrom(4096)

print(data.decode())
client.close()
