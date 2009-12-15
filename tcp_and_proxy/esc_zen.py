#!/usr/bin/python -u

import os
import socket
import struct
import sys
import select
import fcntl

# main data exchange function
def exchange(s):
  # input:
  # s - socket object
  # return:
  # nothing :)

  # setting every description to be non blocking 
  fcntl.fcntl(s, fcntl.F_SETFL, os.O_NONBLOCK|os.O_NDELAY) 
  fcntl.fcntl(0, fcntl.F_SETFL, os.O_NONBLOCK)

  while 1:
    toread,towrite,[]=select.select([sys.stdin,s],[s],[],30)
    
    if s in toread:
      data = s.recv(1500)
      if len(data) == 0:
        s.shutdown(2)
        break
      else:
        sys.stdout.write(data)
    if sys.stdin in toread and s in towrite: 
      data = sys.stdin.read(1500)
      if data:
          s.send(data)

#### main stuff
if __name__ == '__main__':

  if len(sys.argv) >= 2: 
    host = sys.argv[1]
    port = int(sys.argv[2])

    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
      socks.bind((host, port))
    except socket.error:
      sys.stderr.write("[-] problem with binding to "+str(host)+":"+str(port)+"\n")
      socks.close()
      sys.exit()  

    socks.listen(1)
    conn, addr = socks.accept()
    sys.stderr.write("[+] connection accepted from "+str(addr[0])+":"+str(addr[1])+"\n")
    exchange(conn)
    conn.close()
  else:
    sys.stderr.write("usage: "+sys.argv[0]+" bind_ip bind_port\n")
