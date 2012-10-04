#!/usr/bin/python

# $Id: 20121004$
# $Date: 2012-10-04 21:48:47$
# $Author: Marek Lukaszuk$

import socket,time,sys,struct
from select import select

IP = "0.0.0.0"
PORT = 5005

maxlen = 1020 # data size + 2 bytes for header
seq = 1 # our sequence number
ack = 1 # seq number of the peer
notyet = 0 # we didn't yet received an ack from peer
maxmiss = 4 # how many rtts we can wait till resending pkt
paddlen = 251
headsize = 5

# simple diffie-hellman
class DH:
  def __init__(self,p,g):
    self.p = p
    self.g = g
    self.a = randint(1,2**16)
    self.X = (self.g**self.a)%self.p
  def calc_s(self,B):
    # we narrow down the output to only values between 1 and 255
    self.s = (((B**self.a)%self.p) % 255)+1

def encode_head(seq,ack,size,moredata=0):
  return struct.pack("BBHB",seq,ack,size+headsize,moredata)

def decode_head(dat):
  return struct.unpack("BBHB",dat)

def incseq(seq):
  return ((seq + 7) % 255) + 1

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

# our listening socket - blocking
sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
sock.bind((IP,PORT))
sock.setblocking(1)

# this is the start value for to which we will compare
# connecting hosts to know if there is a new connection or not
caddr = ("",0)

srvdata = ""

# lets get some random padding
padding = open("/dev/urandom").read(paddlen)

while True:
  try:
    # this is a blocking socket
    data, addr = sock.recvfrom(maxlen+headsize)
  except socket.error :
    # there was nothing to read from the socket
    if notyet < maxmiss and not caddr == ("",0):
      # we didn't yet got any response
      notyet += 1
    elif notyet == maxmiss:
      # our packet was probably lost, resend
      sys.stderr.write("[!] packet lost, resending\n")
      sending(padding,sock,caddr,seq,ack,srvdata,paddlen,checkformoredata(serv))
      notyet += 1
    elif notyet > maxmiss*3:
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
    # client sent something
    # is this the same client we supposed to talk to
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
      serv.connect( ("127.0.0.1",22))
      # new padding
      padding = open("/dev/urandom").read(paddlen)
      caddr = addr
      seq = 1 # resetting seq number
      head = decode_head(xored(seq,data[:headsize]))
      seq = head[1]

    # decoding header
    head = decode_head(xored(seq,data[:headsize]))
    if seq == head[1]:

      ack = head[0]
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
          sending(padding,sock,caddr,seq,ack,srvdata,paddlen,checkformoredata(serv))
          notyet = 1
      else:
        # if server has nothing to send we need to send a ack
        if seq == 240: # refresh padding
          padding = open("/dev/urandom").read(paddlen)
        sending(padding,sock,caddr,seq,ack,"",paddlen)
        notyet = 1

    else:
      sys.stderr.write("[!] wrong seq\n")

