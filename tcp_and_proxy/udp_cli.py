#!/usr/bin/python -u

import socket
from select import select
import sys
from fcntl import fcntl, F_SETFL
from os import O_NONBLOCK
import time
import struct
from random import randint

IP = sys.argv[1]
PORT = 5005

maxlen = 1020 # data size + 2 bytes for header
seq = randint(1,255) # our sequence number
ack = 1 # seq number of the peer
rtt = 0.1 # round trip time of the pkt
snt = 1 # last time a pkt was send
notyet = 1 # we didn't yet received an ack from peer 
maxmiss = 4 # how many rtts we can wait till resending pkt 
maxif = 10 # max pkts in flight
cif = 0 # current number of pkts in flight
lseq = 0 # oldest seq number
headsize = 4

buff = {} 

def dtime(lt,dt):
  if time.time()-lt > dt:
    return True
  return False

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
sock.setblocking(0)
fcntl(0, F_SETFL, O_NONBLOCK)

dstaddr = (IP,PORT)

padding = open("/dev/urandom").read(256)

snt = sending(padding,sock,dstaddr,seq,ack,"")

clidata = ""

while True:
  toread,towrite,[] = select([0],[1],[],10)

  if 1 in towrite:
    try:
      data, addr = sock.recvfrom (maxlen+headsize)
    except socket.error:
      select([],[],[],rtt)
      if notyet > 0:
        notyet += 1
      if notyet == maxmiss:
        snt = sending(padding,sock,dstaddr,seq,ack,clidata)
      if notyet > maxmiss*3:
        sys.stderr.write("[!] packet lost, exiting\n")
        sys.exit(1)
    else:
      if addr == dstaddr:
        head = decode_head(xored(seq,data[:headsize]))
        if seq == head[1]:
          ack = head[0]
          rtt = calcrtt(snt)
          notyet = 0
          if head[2] > 0 \
              and len(data[headsize:head[2]]) == head[2] - headsize: 
            sys.stdout.write(xored(seq,data[headsize:head[2]]))
          seq = incseq(seq)
        else:
          sys.stderr.write("[!] wrong seq\n")
      else:
        sys.stderr.write("[!] wrong source address: "+str(addr)+"\n")

  if 0 in toread and notyet == 0:
    clidata = sys.stdin.read(maxlen)
    if len(clidata) == 0:
      sys.exit()
    
    else:
      snt = sending(padding,sock,dstaddr,seq,ack,clidata)
      notyet = 1

  if dtime(snt,rtt) and notyet == 0:
    snt = sending(padding,sock,dstaddr,seq,ack,"")
    notyet = 1

