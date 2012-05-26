#!/usr/bin/python

import socket
import time
import sys
import random

count = 5
try:
  count = int(sys.argv[1])
except:
  pass

timem = 1000000
goodenough = 30000 # delay of ans in us
servers = [] 

socket.setdefaulttimeout(2)

def testserver(srv,timem):
  ctime = timem 
  s = socket.socket()
  try:
    stime = time.time()
    s.connect((server,8074))
    etime = time.time()
    s.close()
    return int((etime-stime)*timem)
  except socket.error:
    return timem*10

if __name__ == '__main__':

  # generate all the IPs
  for o4 in xrange(2,100):
    servers.append("91.214.237."+str(o4))

  # test servers
  while len(servers) > 0:

    # pick a random server
    server = random.choice(servers)
    servers.remove(server)

    times = ""
    ok = 1

    # test it if it is ok 3 times
    for i in xrange(0,3):
      delay = testserver(server,timem)
      if delay > goodenough:
        ok = 0
        break
      else:
        times += str(delay)+"us "

    if ok == 1:
      print str(server)+" "+str(times)
      break
    else:
      continue
