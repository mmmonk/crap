#!/usr/bin/python -u

# $Id$

import os
import socket
import struct
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
#  fcntl.fcntl(s, fcntl.F_SETFL, os.O_NONBLOCK)
  fcntl.fcntl(s, fcntl.F_SETFL, os.O_NONBLOCK|os.O_NDELAY) 
  fcntl.fcntl(0, fcntl.F_SETFL, os.O_NONBLOCK)

  s_recv = s.recv
  s_send = s.send
  write  = sys.stdout.write
  read   = sys.stdin.read  
  nagle  = 0

  while 1:
    toread,[],[] = select.select([0,s],[],[],1)
    [],towrite,[] = select.select([],[1,s],[],1)
    
    if 1 in towrite and s in toread:
      data0 = s_recv(4096)
      if len(data0) == 0:
        s.shutdown(2)
        break
      else:
        write(data0)

    if 0 in toread and s in towrite: 
      if nagle == 0:
        data1 = read(4096)
      else:
        data1 += read(4096)
      if nagle == 0 and len(data1) < 768:
        nagle = 1
      elif data1:
        nagle = 0
        s_send(data1)

#### main stuff ####
if __name__ == '__main__':

  if len(sys.argv) >= 2: 
    host = sys.argv[1]
    port = int(sys.argv[2])

    nagle = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
      nagle.connect((host, port))
    except socket.error:
      sys.stderr.write("[-] problem connecting to "+str(host)+":"+str(port)+"\n")
      nagle.close()
      sys.exit()  

    exchange(nagle)
    nagle.close()
  
  else:
    sys.stderr.write("usage: "+sys.argv[0]+" ip_dest port_dest\n")
