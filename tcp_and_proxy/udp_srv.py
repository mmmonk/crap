#!/usr/bin/python

import socket
import time
from select import select
import sys
import struct

IP = "0.0.0.0"
PORT = 5005

maxlen = 1020 # data size + 2 bytes for header
seq = 1 # our sequence number
ack = 1 # seq number of the peer
rtt = 0.1 # round trip time of the pkt
snt = time.time() # last time a pkt was send
notyet = 0 # we didn't yet received an ack from peer
maxmiss = 4 # how many rtts we can wait till resending pkt 
paddlen = 256
headsize = 4

def encode_head(seq,ack,size):
  return struct.pack("BBH",seq,ack,size+headsize)

def decode_head(dat):
  return struct.unpack("BBH",dat)

def incseq(seq):
  seq += 1
  if seq > 255:
    return 1 
  return seq

def calcrtt(snt):
  rtt = round(time.time() - snt,3)
  if rtt < 0.2:
    return 0.2
  if rtt > 1:
    return 1 
  return rtt

def xored(x,msg):
  return "".join([ chr(ord(c)^x) for c in msg ])

def debug(msg):
  sys.stderr.write(msg+"\n")

def sending(pad,sock,dstaddr,seq,ack,data):
  size = len(data)
  if size < 252:
    data += pad[:252-size]
  sock.sendto(xored(ack,encode_head(seq,ack,size)+data),dstaddr)
  return time.time()


sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
sock.bind((IP,PORT))
sock.setblocking(0)

caddr = ("",0)

srvdata = ""

padding = open("/dev/urandom").read(256)

while True:
  try:
    data, addr = sock.recvfrom(maxlen+headsize)
  except socket.error :
    select([],[],[],rtt)
    if notyet > 0 and not caddr == ("",0) :
      notyet += 1
    if notyet == maxmiss:
      sys.stderr.write("[!] packet lost, resending\n")
      snt = sending(padding,sock,caddr,seq,ack,srvdata)
    if notyet > maxmiss*3:
      sys.stderr.write("[!] packet lost, reseting\n")
      caddr = ("",0)
      notyet = 0
      try:
        serv.shutdown(socket.SHUT_RDWR)
      except NameError:
        pass
      except socket.error:
        pass
  else:
    if not addr == caddr:
      try:
        serv.shutdown(socket.SHUT_RDWR)
      except NameError:
        pass
      except socket.error:
        pass
      serv = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
      rtt = 0.1
      snt = time.time() - rtt
      serv.connect( ("127.0.0.1",22))
      padding = open("/dev/urandom").read(256)
      caddr = addr
      head = decode_head(xored(seq,data[:headsize]))
      seq = head[1]

    head = decode_head(xored(seq,data[:headsize]))
    if seq == head[1]:
      ack = head[0]
      rtt = calcrtt(snt)
      toread,towrite,[] = select([serv],[serv],[],10)
      if serv in towrite \
          and head[2] > 0 \
          and len(data[headsize:head[2]]) == head[2]-headsize:
        serv.send(xored(seq,data[headsize:head[2]]))
      seq = incseq(seq)

      if serv in toread:
        srvdata = serv.recv(maxlen)
        if len(srvdata) == 0:
          serv.shutdown(socket.SHUT_RDWR)
          sys.exit()
        else:
          snt = sending(padding,sock,caddr,seq,ack,srvdata)
          notyet = 1
      else:
        snt = sending(padding,sock,caddr,seq,ack,"")
        notyet = 1

    else:
      sys.stderr.write("[!] wrong seq\n")
