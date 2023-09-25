import socket

target_host = "127.0.0.1"
target_port = 9998

# create socket object
# AF_INET参数表示使用标准的IPv4地址或主机名，SOCK_STREAM表示TCP连接
# SOCK_DGRAM表示UDP连接
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect
client.connect((target_host, target_port))

# send data
client.send(b"hello,go")

# receive data
respones = client.recv(4096)

print(respones.decode())
client.close()