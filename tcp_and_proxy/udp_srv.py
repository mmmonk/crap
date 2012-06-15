#!/usr/bin/python

import socket
import time
from select import select
import sys
import struct

def encode_head(seq,ack):
  return struct.pack("BB",seq,ack)

def decode_head(dat):
  return struct.unpack("BB",dat)

def incseq(seq):
  seq += 1
  if seq > 255:
    return 0
  return seq

def calcrtt(snt):
  rtt = round(time.time() - snt,3)
  if rtt < 0.1:
    return 0.1
  if rtt > 1:
    return 1 
  return rtt

def debug(msg):
  sys.stderr.write(msg+"\n")


IP="127.0.0.1"
PORT=5005

maxlen = 1022 # data size + 2 bytes for header
seq = 0 # our sequence number
ack = 0 # seq number of the peer
rtt = 0.1 # round trip time of the pkt
snt = time.time() # last time a pkt was send

sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
sock.bind((IP,PORT))
sock.setblocking(0)

caddr = ("",0)

while True:
  try:
    data, addr = sock.recvfrom(maxlen+2) # +2 because of the header
  except socket.error:
    select([],[],[],rtt)
  else:
    if not addr == caddr:
      try:
        serv.shutdown(socket.SHUT_RDWR)
      except NameError:
        pass
      
      serv = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
      rtt = 0.1
      snt = time.time() - rtt
      serv.connect( (IP,22) )
      caddr = addr
      head = decode_head(data[:2])
      seq = head[1]

    head = decode_head(data[:2]) 
    if seq == head[1]:
      ack = head[0]
      seq = incseq(seq) 
      rtt = calcrtt(snt)
      toread,towrite,[] = select([serv],[serv],[],10)
      if serv in towrite and len(data[2:])>0:
        serv.send(data[2:])
      
      if serv in toread:
        servdata = serv.recv(maxlen)
        if len(servdata) == 0:
          serv.shutdown(socket.SHUT_RDWR)
          sys.exit()
        else:
          sock.sendto(encode_head(seq,ack)+servdata,addr)
          snt = time.time()
          send = 1
      else:
        sock.sendto(encode_head(seq,ack),addr)
        snt = time.time()

    else:
      sys.stderr.write("[!] wrong seq\n")
