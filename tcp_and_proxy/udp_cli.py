#!/usr/bin/python -u

import socket
from select import select
import sys
from fcntl import fcntl, F_SETFL
from os import O_NONBLOCK
import time
import struct

def dtime(lt,dt):
  if time.time()-lt > dt:
    return True
  return False

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

def xored(msg):
  return "".join([ chr(ord(c)^170) for c in msg ])

def debug(msg):
  sys.stderr.write(msg+"\n")

IP = sys.argv[1]
PORT = 5005

maxlen = 1022 # data size + 2 bytes for header
seq = 0 # our sequence number
ack = 0 # seq number of the peer
rtt = 0.1 # round trip time of the pkt
snt = 1 # last time a pkt was send
notyet = 1 # we didn't yet received an ack from peer 
maxmiss = 4 

dstaddr = (IP,PORT)
sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
sock.setblocking(0)

fcntl(0, F_SETFL, O_NONBLOCK)

sock.sendto(encode_head(seq,ack),dstaddr)
snt = time.time() 

clidata = ""

while True:
  toread,towrite,[] = select([0],[1],[],10)

  if 1 in towrite:
    try:
      data, addr = sock.recvfrom (maxlen+2) # +2 because of the header
    except socket.error:
      select([],[],[],rtt)
      if notyet > 0:
        notyet += 1
      if notyet == maxmiss:
        sock.sendto(encode_head(seq,ack)+xored(clidata),dstaddr)
        snt = time.time()
      if notyet > maxmiss:
        sys.stderr.write("[!] packet lost, exiting\n")
        sys.exit(1)
    else:
      if addr == dstaddr:
        head = decode_head(data[:2])
        if seq == head[1]:
          if len(data[2:]) > 0:
            sys.stdout.write(xored(data[2:]))
          ack = head[0]
          seq = incseq(seq)
          rtt = calcrtt(snt)
          notyet = 0
        else:
          sys.stderr.write("[!] wrong seq\n")
      else:
        sys.stderr.write("[!] wrong source address: "+str(addr)+"\n")

  if 0 in toread and notyet == 0:
    clidata = sys.stdin.read(maxlen)
    if len(clidata) == 0:
      sys.exit()
    
    else:
      sock.sendto(encode_head(seq,ack)+xored(clidata),dstaddr)
      notyet = 1
      snt = time.time()

  if dtime(snt,rtt) and notyet == 0:
    sock.sendto(encode_head(seq,ack),dstaddr)
    notyet = 1
    snt = time.time()

