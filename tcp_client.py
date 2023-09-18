import socket

target_host = "127.0.0.1"
target_port = 9998

# create socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect
client.connect((target_host, target_port))

# send data
client.send(b"hello,go")

# receive data
respones = client.recv(4096)

print(respones.decode())
client.close()