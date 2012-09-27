#!/usr/bin/python -u

# $Id: 20120926$
# $Date: 2012-09-26 10:14:35$
# $Author: Marek Lukaszuk$

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
paddlen = 251 # 256 - header size
headsize = 5 # header size

buff = {}

# simple diffie-hellman
class DH:
  def __init__(self,p,g):
    self.p = p
    self.g = g
    self.a = randint(1,2**16)
    self.X = (self.g**self.a)%self.p
  def calc_s(self,B):
    # we narrow down the output to only values between 1 and 255
    self.s = (((B**self.a)%self.p) % 254)+1

def dtime(lt,dt):
  if time.time()-lt > dt:
    return True
  return False

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

def sending(pad,sock,dstaddr,seq,ack,data,paddlen):
  size = len(data)
  if size < paddlen:
    data += pad[:paddlen-size]
  sock.sendto(xored(ack,encode_head(seq,ack,size,0)+data),dstaddr)
  return time.time()

# this is socket to our server
sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
sock.setblocking(0) # yep this one is non blocking
fcntl(0, F_SETFL, O_NONBLOCK) # our stdout is also non blocking

# this is our server address and port
dstaddr = (IP,PORT)

# getting some random padding that we will use
padding = open("/dev/urandom").read(paddlen)

# lets send the first empty packet
# ssh starts with a banner from the server
# and we send this packet to get that banner
snt = sending(padding,sock,dstaddr,seq,ack,"",paddlen)

getmore = 0
clidata = ""

while True:
  toread,towrite,[] = select([0],[1],[],10)

  # test to see if there is anything from the server
  if 1 in towrite:
    try:
      # this is done on a non-blocking socket
      data, addr = sock.recvfrom (maxlen+headsize)
    except socket.error:
      # there was nothing to read from the socket
      if notyet > 0 and dtime(snt,rtt):
        # we didn't yet got any response
        notyet += 1
      if notyet == maxmiss:
        # our packet was probably lost, resend
        snt = sending(padding,sock,dstaddr,seq,ack,clidata,paddlen)
        notyet += 1
      if notyet > maxmiss*3:
        # we give up
        sys.stderr.write("[!] packet lost, exiting\n")
        sys.exit(1)
    else:
      # server sent something
      # is this the same server we supposed to talk to
      if addr == dstaddr:
        # lets see the header (after xoring the data)
        head = decode_head(xored(seq,data[:headsize]))
        if seq == head[1]:
          ack = head[0] # set our ack
          rtt = calcrtt(snt) # modify the rtt
          notyet = 0 # we got our packet
          if head[2] > 0 \
              and len(data[headsize:head[2]]) == head[2] - headsize:
            # this packet seems to have a valid data, let see what it is
            sys.stdout.write(xored(seq,data[headsize:head[2]]))
          seq = incseq(seq) # increase our seq num
          getmore = head[3] # is there more data ?
        else:
          sys.stderr.write("[!] wrong seq\n")
      else:
        sys.stderr.write("[!] wrong source address: "+str(addr)+"\n")

  # client has something to send
  if 0 in toread and notyet == 0:
    clidata = sys.stdin.read(maxlen)
    if len(clidata) == 0:
      sys.exit()

    else:
      # client sends data here
      snt = sending(padding,sock,dstaddr,seq,ack,clidata,paddlen)
      notyet = 1 # we need to wait


  # send a packet either to get more data or
  # to check if the server has anything to send
  if (getmore == 1 or dtime(snt,rtt)) and notyet == 0:
    snt = sending(padding,sock,dstaddr,seq,ack,"",paddlen)
    getmore = 0 # lets reset this
    notyet = 1 # we need to wait

  if getmore == 0 and notyet == 1:
    select([],[],[],rtt)
