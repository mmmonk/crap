#!/usr/bin/env python

import sys

da = int(sys.argv[1])

ha=hex(da).replace("0x","").zfill(8)
print str(int(ha[6:8],16))+"."+str(int(ha[4:6],16))+"."+str(int(ha[2:4],16))+"."+str(int(ha[0:2],16))
