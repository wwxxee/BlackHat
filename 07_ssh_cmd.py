import paramiko


def ssh_command(ip, port, user, passwd, cmd):
    # 实例化SSHClient
    client = paramiko.SSHClient()

    # 自动添加策略，保存服务器的主机名和密钥信息，如果不添加，那么不再本地know_hosts文件中记录的主机将无法连接
    # 当服务器发来没有记录的公钥时，我们的策略是自动信任并记住这个公钥
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # 连接SSH服务端，以用户名和密码进行认证
    client.connect(ip, port, user, passwd)

    # 打开一个Channel并执行命令
    stdin, stdout, stderr = client.exec_command(cmd)

    output = stdout.readlines() + stderr.readlines()
    if output:
        print("---output---")
        for line in output:
            print(line.strip())
    client.close()


if __name__ == '__main__':
    import getpass
    user = input("Username:")
    passwd = getpass.getpass()
    ip = input("Enter Server IP:") or '192.168.52.137'
    port = input("Enter port or <CR>") or 22
    cmd = input("Enter command or <CR>") or 'id'
    ssh_command(ip, port, user, passwd, cmd)
