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
paddlen = 251
headsize = 5 

def encode_head(seq,ack,size,moredata=0):
  return struct.pack("BBHB",seq,ack,size+headsize,moredata)

def decode_head(dat):
  return struct.unpack("BBHB",dat)

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

def checkformoredata(sock):
  if sock in (select([sock],[],[],0.1))[0]:
    return 1
  return 0

def sending(pad,sock,dstaddr,seq,ack,data,paddlen,moredata=0):
  size = len(data)
  if size < paddlen:
    data += pad[:paddlen-size]
  sock.sendto(xored(ack,encode_head(seq,ack,size,moredata)+data),dstaddr)
  return time.time()

# our listening socket - non blocking
sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
sock.bind((IP,PORT))
sock.setblocking(0)

# this is the start value for to which we will compare 
# connecting hosts to know if there is a new connection or not
caddr = ("",0)

srvdata = ""

# lets get some random padding
padding = open("/dev/urandom").read(paddlen)

while True:
  try:
    # this is done on a non-blocking socket
    data, addr = sock.recvfrom(maxlen+headsize)
  except socket.error :
    # there was nothing to read from the socket
    # lets wait, is this the best place TODO ??
    select([],[],[],rtt)
    if notyet > 0 and not caddr == ("",0):
      # we didn't yet got any response
      notyet += 1
    if notyet == maxmiss:
      # our packet was probably lost, resend
      sys.stderr.write("[!] packet lost, resending\n")
      snt = sending(padding,sock,caddr,seq,ack,srvdata,paddlen,checkformoredata(serv))
    if notyet > maxmiss*3:
      # we give up
      sys.stderr.write("[!] packet lost, reseting\n")
      # we need to reset some value
      caddr = ("",0)
      notyet = 0
      # and close the tcp connection if it is still active
      try:
        serv.shutdown(socket.SHUT_RDWR)
      except NameError:
        pass
      except socket.error:
        pass
  else:
    # server sent something
    # is this the same server we supposed to talk to
    if not addr == caddr:
      # this is new client connection
      # we need to close the old connection to the server
      try:
        serv.shutdown(socket.SHUT_RDWR)
      except NameError:
        pass
      except socket.error:
        pass
      # and start a new one
      serv = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
      rtt = 0.1
      snt = time.time() - rtt
      serv.connect( ("127.0.0.1",22))
      # new padding
      padding = open("/dev/urandom").read(paddlen)
      caddr = addr
      head = decode_head(xored(seq,data[:headsize]))
      seq = head[1]

    # decoding header
    head = decode_head(xored(seq,data[:headsize]))
    if seq == head[1]:
      ack = head[0]
      rtt = calcrtt(snt)
      toread,towrite,[] = select([serv],[serv],[],10)
      # server allows us to write
      if serv in towrite \
          and head[2] > 0 \
          and len(data[headsize:head[2]]) == head[2]-headsize:
        serv.send(xored(seq,data[headsize:head[2]]))
      seq = incseq(seq) # increasing our seq number

      # server has something to send
      if serv in toread:
        srvdata = serv.recv(maxlen)
        if len(srvdata) == 0:
          serv.shutdown(socket.SHUT_RDWR)
          sys.exit()
        else:
          # sending from server
          snt = sending(padding,sock,caddr,seq,ack,srvdata,paddlen,checkformoredata(serv))
          notyet = 1
      else:
        # if server has nothing to send we need to send a ack
        snt = sending(padding,sock,caddr,seq,ack,"",paddlen)
        notyet = 1

    else:
      sys.stderr.write("[!] wrong seq\n")
