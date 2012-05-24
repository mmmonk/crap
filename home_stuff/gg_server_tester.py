#!/usr/bin/python

import socket
import time

servers = dict() 

socket.setdefaulttimeout(2)

for o4 in xrange(2,100):
  servers["91.214.237."+str(o4)] = 10000

for server in servers:
  s = socket.socket()
  try:
    stime = time.time()
    s.connect((server,8074))
    etime = time.time()
    s.close()
    servers[server]=int((etime-stime)*1000)
  except socket.error:
    pass

best = "91.214.237.2"
for server in servers:
  if servers[server] < servers[best]:
    best = server

print str(best)+" time: "+str(servers[best])+" ms"
