#!/usr/bin/env python

# $Id: 20130125$
# $Date: 2013-01-25 15:34:43$
# $Author: Marek Lukaszuk$

# https://en.wikipedia.org/wiki/Bandwidth-delay_product

import sys
import re
import argparse

p = argparse.ArgumentParser(description='Bandwidth delay product calculator')
p.add_argument('bandwidth',help="bandwitdh of the link, with proper units (default: bits)")
p.add_argument('delay',type=float,help="delay of the link in ms")
p.add_argument('--mtu',type=int,default=1500,help="MTU on that link (default=1500)")

args = p.parse_args()

b = args.bandwidth.lower()
d = args.delay*(10**(-3)) # delay is in ms = 10**-3

if "gb" in b:
  u = 9
elif "mb" in b:
  u = 6 
elif "kb" in b:
  u = 3 
else:
  u = 0 
 
b = float(re.search("^(\d|\.)+",b).group(0))*(10**u)

bdp = int((b*d)/8.0) # converted to bytes

print "BDP: "+str(bdp)+" bytes"
if bdp*2 > 262140:
  print "WAN suggested buffer size: "+str(bdp*2)+" bytes"
  print "Buffers on WAN router: at least "+str(int(round(float(bdp)/args.mtu,0)))+" packets"
else:
  print "defaults are ok"
