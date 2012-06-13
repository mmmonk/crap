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

caddr = ("",0)

while True:
  try:
    data, addr = sock.recvfrom( maxlen )
  except socket.error:
    pass
  else:
    if not addr == caddr: 
      try:
        serv.shutdown(socket.SHUT_RDWR)
      except NameError:
        pass
      serv = socket.socket( socket.AF_INET, socket.SOCK_STREAM ) 
      serv.connect( (UDP_IP,22) )

    caddr = addr

    toread,[],[] = select([serv],[],[],1)
    [],towrite,[] = select([],[serv],[],1)
    if serv in towrite:
      serv.send(data)
    if serv in toread:
      servdata = serv.recv(maxlen)
      if len(servdata) == 0:
        serv.shutdown(socket.SHUT_RDWR)
        sys.exit()
      else:
        sock.sendto(servdata,addr)

