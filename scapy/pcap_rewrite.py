#!/usr/bin/python

from scapy.all import * 
import sys

INpcap = sys.argv[1]
OUTpcap = sys.argv[2]

pkts = rdpcap(INpcap,count=-1)

for pkt in pkts: 
  if pkt[IP].src in "7.158.1.117":
    pkt[IP].setfieldval("src","7.158.123.255")
 
wrpcap(OUTpcap,pkts)
