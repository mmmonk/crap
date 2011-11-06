#!/usr/bin/env python

# $Id$

from scapy.all import conf,sr1,IP,TCP,UDP
import sys
import random
import time

dhost = sys.argv[1] 

shost = "172.30."+str(random.randint(72,73))+"."+str(random.randint(2,254))
sport = random.randint(1025,65534)

portrange = range(1,65535)
for i in xrange(1,65535):
  port = random.choice(portrange)
  print "shost:"+shost+" sport:"+str(sport)+" dport:"+str(port) 
  #send(IP(src=shost,dst=dhost,flags=2,tos=0,ttl=128)/UDP(sport=sport,dport=port)
  send(IP(src=shost,dst=dhost,flags=2,tos=0,ttl=128)/TCP(sport=sport,dport=port,flags=2,urgptr=0))
  portrange.remove(port)
  if i % 10 == 0:
    shost = "172.30."+str(random.randint(72,73))+"."+str(random.randint(2,254))
    sport = random.randint(1025,65534)
    time.sleep(1)
