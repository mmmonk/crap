#!/usr/bin/env python

# $Id: 20130124$
# $Date: 2013-01-24 17:28:29$
# $Author: Marek Lukaszuk$

# https://en.wikipedia.org/wiki/Bandwidth-delay_product

import sys
import re

try:
  b = sys.argv[1].lower()
  d = float(sys.argv[2])
except:
  print "usage: "+str(sys.argv[0])+" bandwidth delay <MTU>\n bandwidth requires units (Gb|Mb|kb)/s, delay is always in ms, MTU by default is 1500"
  sys.exit(1)

try:
  mtu = int(sys.argv[3])
except:
  print "assuming MTU = 1500"
  mtu = 1500

if "gb" in b:
  u1 = 10**9
elif "mb" in b:
  u1 = 10**6 
elif "kb" in b:
  u1 = 10**3 
else:
  u1 = 1 
  
bi = int(re.search("^\d+",b).group(0))

u2 = 10**(-3) # ms
bdp = int(round((bi*u1*d*u2)/8,0))

print "BDP: "+str(bdp)+" bytes"
if bdp*2 > 262140:
  print "WAN Send Buffer Size: "+str(bdp*2)+" bytes"
  print "WAN Receive Buffer Size: "+str(bdp*2)+" bytes"
#  print "LAN Send Buffer Size: "+str(bdp*2.5)+" bytes"
#  print "LAN Receive Buffer Size: "+str(bdp*2.5)+" bytes"
  print "Buffers on WAN router: at least "+str(int(round(float(bdp)/mtu,0)))+" packets"
else:
  print "defaults are ok"
