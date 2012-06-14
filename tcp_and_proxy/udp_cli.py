#!/usr/bin/python -u

import socket
from select import select
import sys
from fcntl import fcntl, F_SETFL
from os import O_NONBLOCK
import time
import struct

def dtime(lt,dt):
  ct = time.time()
  if ct-lt > dt:
    return True
  else:
    return False

def header(seq,ack):
  return struct.pack("BB",seq,ack)

def incseq(seq):
  seq += 1
  if seq > 255:
    return 0
  return seq

def debug(msg):
  sys.stderr.write(msg+"\n")

IP="127.0.0.1"
PORT=5005

maxlen = 1024 # <<- FIXME why this is 2 higher then on the server????
seq = 0
ack = 0
rtt = 1
snt = 1
notyet = 0

dstaddr = (IP,PORT)
sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
sock.setblocking(0)

fcntl(0, F_SETFL, O_NONBLOCK)

sock.sendto(header(seq,ack),dstaddr)

lt = time.time()

while True:
  toread,towrite,[] = select([0],[1],[],10)

  if 1 in towrite:
    try:
      data, addr = sock.recvfrom (maxlen)
    except socket.error:
      select([],[],[],0.2)
      pass
    else:
      if addr == dstaddr:
        head = struct.unpack("BB",data[:2])
        if seq == head[1]:
          if len(data[2:]) > 0:
            sys.stdout.write(data[2:])
          ack = head[0]
          seq = incseq(seq)
          #rtt = time.time() - snt
          notyet = 0
        else:
          sys.stderr.write("[!] wrong seq\n")
      else:
        sys.stderr.write("[!] wrong source address: "+str(addr)+"\n")

  if 0 in toread and notyet == 0:
    si = sys.stdin.read(maxlen)
    if len(si) == 0:
      sys.exit()
    
    else:
      sock.sendto(header(seq,ack)+si,dstaddr)
      notyet = 1
      lt = time.time()
      snt = lt

  if dtime(lt,0.1) and notyet == 0:
    sock.sendto(header(seq,ack),dstaddr)
    notyet = 1
    snt = time.time()
