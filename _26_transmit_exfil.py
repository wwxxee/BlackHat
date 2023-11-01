import ftplib
import os
import socket
import win32file


def plain_ftp(docpath, server=''):
    ftp = ftplib.FTP(server)
    ftp.login("anonymous", "password")

    # 设置服务器端的当前目录。
    ftp.cwd('/pub/')

    # 以二进制传输模式存储文件。
    ftp.storbinary("STOR" + os.path.basename(docpath), open(docpath, "rb"), 1024)
    # 向服务器发送 QUIT 命令并关闭连接
    ftp.quit()


def transmit(document_path):
    client = socket.socket()
    client.connect(('192.168.1.1', 10000))
    with open(document_path, 'rb') as f:
        win32file.TransmitFile(client, win32file._get_osfhandle(f.fileno()), 0, 0, None, 0, b'', b'')


if __name__ == '__main__':
    transmit('./test.txt')

