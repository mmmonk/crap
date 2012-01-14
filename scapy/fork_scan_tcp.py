#!/usr/bin/env python

# $Id$

from scapy.all import conf,IP,TCP,sr1,sniff,send
conf.verb = 0 

from time import sleep
import sys
import os


# TODO
# add logic to support subnets (IPv4/IPv6)
# add range of ports
# randomize asking

host = sys.argv[1]
port = int(sys.argv[2])

# TODO
# make this a bit more uniq - MD5(str(host)+str(port)+str(salt)) ?
def seqgen(host,port):
  return 1234

# TODO
# check here also if the TCP packet is SYN+ACK
def checkpkt(pkt):
  if pkt.haslayer(TCP):
    nack = (pkt.getlayer(TCP).ack)-1
    if nack == 1234:
      return True
    else:
      return False
  else:
    return False

if os.fork():
  # TODO
  # print packets directly from sniff (check scapy docs) don't store them
  pkts = sniff(filter="ip and tcp", timeout = 15, lfilter= lambda x: checkpkt(x))
  print pkts.summary()

else:
  sleep(1)
  pkt = IP(dst=host)/TCP(dport=port,seq=seqgen(host,port))
  send(pkt)

try:
  os.wait()
except:
  pass
