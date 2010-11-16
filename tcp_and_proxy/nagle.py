#!/usr/bin/python -u

# $Id$

import os
import socket
import sys
import select
import fcntl

# main data exchnage function
def exchange(s):
  # input:
  # s - socket object
  # return:
  # nothing :)

  # setting every descriptor to be non blocking 
  fcntl.fcntl(s, fcntl.F_SETFL, os.O_NONBLOCK) 
  fcntl.fcntl(0, fcntl.F_SETFL, os.O_NONBLOCK)

  s_recv = s.recv
  s_send = s.send
  write  = sys.stdout.write
  read   = sys.stdin.read  

  while 1:
    toread,[],[] = select.select([0,s],[],[],30)
    [],towrite,[] = select.select([],[1,s],[],30)
    
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

    tcpcork = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpcork.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK,1)
    try:
      tcpcork.connect((host, port))
    except socket.error:
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
