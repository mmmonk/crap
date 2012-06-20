#!/usr/bin/python

import socket
from time import time
from sys import exit
from random import choice as rndchoice
from os import getenv

timem = 1000000
goodenough = 60000 # delay of ans including reading 2 first bytes in us
servers = [] 

socket.setdefaulttimeout(2)

def testserver(srv,timem):
  s = socket.socket()
  try:
    stime = time()
    s.connect((server,8074))
    data = s.recv(2)
    if str(data).encode('hex') == "0100":
      etime = time()
    else:
      etime = stime + timem*10
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
    server = rndchoice(servers)
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
      try:
        open(str(getenv('HOME'))+"/.gg/cmd","w").write("\
            /set server "+str(server)+"\n\
            /wr\n\
            /reconnect\n\
            /echo \""+str(server)+" "+str(times)+"\n")
      except:
        exit(1)
      break
    else:
      continue
