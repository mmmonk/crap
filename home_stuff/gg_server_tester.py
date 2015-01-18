#!/usr/bin/python

import socket
from time import time,sleep
from sys import exit
from random import choice as rndchoice
from os import getenv

servers = []
socket.setdefaulttimeout(3)

def testserver(srv):
  s = socket.socket()
  try:
    start_time = time()
    s.connect((srv,8074))
    data = s.recv(2)
    s.close()
    conn_time = time()-start_time
    if str(data).encode('hex') == "0100":
      return conn_time 
    return 0 
  except socket.error:
    return 0

def useserver(srv):
  try:
    open(str(getenv('HOME'))+"/.gg/cmd","w").write(
      "/set server %s\n" % (srv) +\
      "/wr\n/reconnect\n/beep\n")
    exit(0)
  except:
    exit(1)

if __name__ == '__main__':

  # generate all the IPs
  for o4 in xrange(2,100):
    servers.append("91.214.237."+str(o4))

  alive = {}
  # test servers
  while len(servers) > 0:

    # pick a random server
    server = rndchoice(servers)
    servers.remove(server)

    result = testserver(server)
    if result > 0:
      alive[server] = result
      if result <= 0.05:
        print server
        useserver(server)

  tmpsrv = sorted(alive.iteritems(), key=lambda srv: srv[1])
  alive = [item[0] for item in tmpsrv]
  useserver(rndchoice(alive))
