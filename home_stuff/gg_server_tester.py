#!/usr/bin/python

import socket
import time
import sys

count = 5
try:
  count = int(sys.argv[1])
except:
  pass

servers = dict() 

socket.setdefaulttimeout(2)

for o4 in xrange(2,100):
  servers["91.214.237."+str(o4)] = 10000000

for server in servers:
  s = socket.socket()
  try:
    stime = time.time()
    s.connect((server,8074))
    etime = time.time()
    s.close()
    servers[server]=int((etime-stime)*1000000)
  except socket.error:
    pass

a = sorted(servers.items(),key=lambda x: x[1])
for i in xrange(0,count):
  print str(a[i][0]).ljust(14)+" time: "+str(a[i][1])+" us"
