#!/usr/bin/python -u

import socket
from select import select
import sys
from fcntl import fcntl, F_SETFL
from os import O_NONBLOCK

UDP_IP="127.0.0.1"
UDP_PORT=5005

sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
sock.setblocking(0)

fcntl(0, F_SETFL, O_NONBLOCK)

while True:
  toread,[],[] = select([0],[],[],1)
  [],towrite,[] = select([],[1],[],1)

  if 1 in towrite:
    try:
      data, addr = sock.recvfrom ( 1024 )
    except socket.error:
      pass
    else:
      sys.stdout.write(data)

  elif 0 in toread:
    si = sys.stdin.read(1024)
    if len(si) == 0:
      sys.exit()
    else:
      sock.sendto(si,(UDP_IP,UDP_PORT))
