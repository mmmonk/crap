#!/usr/bin/python

import socket
import time
from select import select
import sys
import struct

def header(seq,ack):
  return struct.pack("BB",seq,ack)

def incseq(seq):
  seq += 1
  if seq > 255:
    return 0
  return seq

def debug(msg):
  sys.stderr.write(msg+"\n")

maxlen = 1022

IP="127.0.0.1"
PORT=5005

sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
sock.bind((IP,PORT))
sock.setblocking(0)

seq = 0
ack = 0
rtt = 1
snt = 1

caddr = ("",0)

while True:
  try:
    data, addr = sock.recvfrom( maxlen )
  except socket.error:
    select([],[],[],0.1)
    pass
  else:
    if not addr == caddr: 
      try:
        serv.shutdown(socket.SHUT_RDWR)
      except NameError:
        pass
      serv = socket.socket( socket.AF_INET, socket.SOCK_STREAM ) 
      serv.connect( (IP,22) )
      head = struct.unpack("BB",data[:2])
      seq = head[1]

    caddr = addr
    head = struct.unpack("BB",data[:2])

    if seq == head[1]:
      ack = head[0]
      seq = incseq(seq) 
      send = 0
      toread,towrite,[] = select([serv],[serv],[],10)
      if serv in towrite and len(data[2:])>0:
        serv.send(data[2:])
      if serv in toread:
        servdata = serv.recv(maxlen)
        if len(servdata) == 0:
          serv.shutdown(socket.SHUT_RDWR)
          sys.exit()
        else:
          sock.sendto(header(seq,ack)+servdata,addr)
          send = 1

      if send == 0:
        sock.sendto(header(seq,ack),addr)
    else:
      sys.stderr.write("[!] wrong seq\n")
