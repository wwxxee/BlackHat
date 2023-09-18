import argparse
from dataclasses import dataclass
import socket
import shlex
import subprocess
import sys
import textwrap
import threading
from urllib import response


def execute(cmd):
    cmd=cmd.strip()
    if not cmd:
        return
    output=subprocess.check_output(shlex.split(cmd),stderr=subprocess.STDOUT)
    return output.decode()

class NetCat:
   def __init__(self,args,buffer=None):
       self.args=args
       self.buffer=buffer
       self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
       self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    
   def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

   def send(self):
       self.socket.connect((self.args.target,self.args.port))
       if self.buffer:
           self.socket.send(self.buffer)
       try:
            while True:
                recv_len=1
                response=''
                while recv_len:
                    data=self.socket.recv(4096)
                    recv_len=len(data)
                    response+=data.decode()
                    #modity recv_len <2
                    if recv_len< 2:
                        break
                    if response:
                        print(response)
                        buffer=input('BHP:#>')
                        buffer+='\n'
                        self.socket.send(buffer.encode())
       except KeyboardInterrupt:
            print('User terminated.')
            self.socket.close()
            sys.exit()

   def listen(self):
       self.socket.bind((self.args.target,self.args.port))
       self.socket.listen(5)

       while True:
           client_sock,_=self.socket.accept()
           client_handler=threading.Thread(target=self.client_handle,args=(client_sock,))
           client_handler.start()

   def client_handle(self,client_sock):
       if self.args.execute:
           output=execute(self.args.execute)
           client_sock.send(output.encode())
       elif self.args.upload:
           file_buffer=b''
           while True:
               data=client_sock.recv(4096)
               if data:
                   file_buffer+=data
               else:
                   break
           with open(self.args.upload,'wb') as f:
               f.write(file_buffer)
           message=f'Save file {self.args.upload}'
           client_sock.send(message.encode())

       elif self.args.command:
           cmd_buffer=b''
           while True:
               try:
                   client_sock.send(b'BHP:#>')
                   while '\n' not in cmd_buffer.decode():
                       data=client_sock.recv(4096)
                       cmd_buffer+=data
                   response=execute(cmd_buffer.decode())
                   if response:
                        client_sock.send(response.encode())
                   cmd_buffer=b''
               except Exception as e:
                   print(f'server kill {e}')
                   self.socket.close()
                   sys.exit()

if __name__=="__main__":
    parse=argparse.ArgumentParser(description="BHP Net Tool",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=textwrap.dedent('''Example:
    netcat.py -t 192.168.88.132 -p 9998 -l -c #command shell
    netcat.py -t 192.168.88.132 -p 9998 -l -u=tests.txt #upload file
    netcat.py -t 192.168.88.132 -p 9998 -l -e=\"cat /etc/passwd\" # execute command
    echo -ne 'GET / HTTP/1.1\r\nHOST:baidu.com\r\n\r\n' | python 02/netcat.py -t www.baidu.com  -p 80 #echo text to server port 135
    netcat.py -t 192.168.88.132 -p 9998 #connect server
    '''
    ))
    parse.add_argument('-c','--command',action='store_true',help='command shell')
    parse.add_argument('-e','--execute',help='execute specified command')
    parse.add_argument('-l','--listen',action='store_true',help='listen')
    parse.add_argument('-p','--port',type=int,default=5555,help='specified port')
    parse.add_argument('-t','--target',default='192.168.88.132',help='specified ip')
    parse.add_argument('-u','--upload',help='upload file')

    args=parse.parse_args()

    if args.listen:
        buffer=''
    else:
        buffer=sys.stdin.read()

    nc=NetCat(args,buffer.encode())
    nc.run()


