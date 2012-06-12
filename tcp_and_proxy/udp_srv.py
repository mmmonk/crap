#!/usr/bin/python

import socket
import time
from select import select
import sys

maxlen = 1024

UDP_IP="127.0.0.1"
UDP_PORT=5005

sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
sock.bind( (UDP_IP,UDP_PORT) )
sock.setblocking(0)

serv = socket.socket( socket.AF_INET, socket.SOCK_STREAM ) 
serv.connect( (UDP_IP,22) )

while True:
  try:
    data, addr = sock.recvfrom( maxlen )
  except socket.error:
    pass
  else:
    toread,[],[] = select([serv],[],[],1)
    [],towrite,[] = select([],[serv],[],1)
    if serv in towrite:
      serv.write(data)
    elif serv in toread:
      servdata = serv.read(maxlen)
      if len(servdata) == 0:
        serv.shutdown()
        sys.exit()
      else:
        sock.sendto(servdata,addr)

