#!/usr/bin/python -u

# $Id$

from os import O_NONBLOCK 
from socket import socket,AF_INET,SOCK_STREAM,IPPROTO_TCP,TCP_CORK,error
import sys
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
  write  = sys.stdout.write
  read   = sys.stdin.read  

  while 1:
    toread,[],[] = select([0,s],[],[],30)
    [],towrite,[] = select([],[1,s],[],30)
    
    if 1 in towrite and s in toread:
      data = s_recv(4096)
      if len(data) == 0:
        s.shutdown(2)
        sys.exit()
        break
      else:
        write(data)

    elif 0 in toread and s in towrite: 
      data = read(4096)
      if len(data) == 0:
        sys.exit()
      else: 
        s_send(data)

#### main stuff ####
if __name__ == '__main__':

  if len(sys.argv) >= 2: 
    host = sys.argv[1]
    port = int(sys.argv[2])

    tcpcork = socket(AF_INET, SOCK_STREAM)
    tcpcork.setsockopt(IPPROTO_TCP, TCP_CORK,1)
    try:
      tcpcork.connect((host, port))
    except error:
      sys.stderr.write("[-] problem connecting to "+str(host)+":"+str(port)+"\n")
      tcpcork.close()
      sys.exit()  

    try:
      exchange(tcpcork)
    except KeyboardInterrupt:
      pass      

    tcpcork.close()
  
  else:
    sys.stderr.write("usage: "+sys.argv[0]+" ip_dest port_dest\n")
