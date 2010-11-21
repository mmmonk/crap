#!/usr/bin/python -u

# $Id$

from os import O_NONBLOCK 
from socket import socket,AF_INET,SOCK_STREAM,IPPROTO_TCP,TCP_CORK,error as sock_error
from sys import stdin, stdout, stderr, exit, argv
from select import select
from fcntl import fcntl,F_SETFL

# main data exchnage function
def exchange(s):
  # input:
  # s - socket object
  # return:
  # nothing :)

  # setting every descriptor to be non blocking 
  fcntl(s, F_SETFL, O_NONBLOCK) 
  fcntl(0, F_SETFL, O_NONBLOCK)

  s_recv = s.recv
  s_send = s.send
  write  = stdout.write
  read   = stdin.read  

  while 1:
    toread,[],[] = select([0,s],[],[],30)
    [],towrite,[] = select([],[1,s],[],30)
    
    if 1 in towrite and s in toread:
      data = s_recv(4096)
      if len(data) == 0:
        s.shutdown(2)
        exit()
        break
      else:
        write(data)

    elif 0 in toread and s in towrite: 
      data = read(4096)
      if len(data) == 0:
        exit()
      else: 
        s_send(data)

#### main stuff ####
if __name__ == '__main__':

  if len(argv) >= 3:
    host = argv[1]
    port = int(argv[2])

    tcpcork = socket(AF_INET, SOCK_STREAM)
    tcpcork.setsockopt(IPPROTO_TCP, TCP_CORK,1)
    try:
      tcpcork.connect((host, port))
    except sock_error:
      stderr.write("[-] problem connecting to "+str(host)+":"+str(port)+"\n")
      tcpcork.close()
      exit()  

    try:
      exchange(tcpcork)
    except KeyboardInterrupt:
      pass      

    tcpcork.close()
  
  else:
    stderr.write("usage: "+argv[0]+" ip_dest port_dest\n")
