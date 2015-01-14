#!/usr/bin/env python

import sys
from scapy.all import *

"""
usage: ./scriptname.py <ipv4 address to test>
"""

def find_out_if(ipv4):
  ipv4 = int("".join([chr(int(i)) for i in ipv4.split('.')]).encode('hex'),16)
  for route in sorted(read_routes(), key=lambda x: x[1], reverse=True):
    if ipv4 & route[1] == route[0]: return route[3]
  return "?"

print find_out_if(sys.argv[1]) 
