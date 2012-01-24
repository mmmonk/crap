#!/usr/bin/env python

# $Id$

from scapy.all import conf,IP,TCP,sr1,sniff,send
conf.verb = 0

import random
import re
import sys

my_ttl = 1
try:
  target = sys.argv[1]
  my_dport = int(sys.argv[2])
except:
  print "usage: "+sys.argv[0]+" host port"
  sys.exit(1)

def dec2bin(a,b):
  if a == 0:
	return 0
  else:
	b.append(a % 2)
	dec2bin((int)(a / 2),b)

def TCPflags(a):
  flags = ['F','S','R','P','A','U','E','C']
  tcpflags = []
  bin(a)
  dec2bin(a,tcpflags)

  retval = ""

  i = 0
  for val in tcpflags:
	if val == 1:
	  retval = retval+flags[i]
	i = i+1

  return retval 

pkts = "" 
while 1 == 1:
  tmp = sniff(filter="ip and tcp and src port "+str(my_dport)+" and src host "+str(target),timeout = 5, count = 1, lfilter = lambda x: x.haslayer(TCP))
  if len(tmp) > 0:
    pkts = tmp
  else:
    if len(pkts) > 0:
      break

pkts.nsummary()

lpkt = pkts[0]

try:
  my_ack = lpkt.seq+len(lpkt.load)
except:
  my_ack = lpkt.seq

### got timestamp

tseho = 0
for opt in lpkt.getlayer(TCP).options:
  if "Timestamp" in opt:
    tseho = opt[1][0]

tsval = tseho + 3


my_seq = lpkt.ack
my_sport = lpkt.dport 
dttl = lpkt.ttl

print "got TCP flags %s and TTL %d from target %s" % (TCPflags(lpkt.getlayer(TCP).flags),dttl,target)
print "using: seq: "+str(my_seq)+", ack:"+str(my_ack)+", sport:"+str(my_sport)

ttldiff = 255
for defttl in [64,128,255]:
  tmp = defttl-dttl
  if tmp > 0 and tmp < ttldiff:
	ttldiff = tmp

print "%s is probably %d hops away (at least one way ;))" % (target,ttldiff+1)

pkt = IP(dst = target)/TCP(sport = my_sport, dport = my_dport, flags = "A", seq = my_seq, ack = my_ack)

if tseho > 0:
  pkt.payload.options = [('NOP', None), ('NOP', None),('Timestamp',(tsval,tseho))]

while 1 == 1:
  pkt.ttl = my_ttl
  rcv = sr1(pkt,retry = 2,timeout = 1)
  if rcv:
    print "%2d : %15s rcv proto %s, TTL %3d" % (my_ttl,rcv.src,rcv.proto,rcv.ttl)

    if rcv.haslayer(TCP):
      print "done, got: TCP flags: %s" % TCPflags(rcv.getlayer(TCP).flags)
      break

  else:
    print "%2d : ???.???.???.???" % my_ttl
    if my_ttl > 20:
      print "out of TTL ;)"
      break
  
  my_ttl = my_ttl+1
