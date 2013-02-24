#!/usr/bin/env python

import sys

ha = sys.argv[1]

print str(int(ha[0:2],16))+"."+str(int(ha[2:4],16))+"."+str(int(ha[4:6],16))+"."+str(int(ha[6:8],16))
