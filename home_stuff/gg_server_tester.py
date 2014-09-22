#!/usr/bin/python

import socket
from time import time,sleep
from sys import exit
from random import choice as rndchoice
from os import getenv

servers = []

socket.setdefaulttimeout(5)

def testserver(srv):
  s = socket.socket()
  try:
    start_time = time()
    s.connect((srv,8074))
    data = s.recv(2)
    s.close()
    conn_time = time()-start_time
    if str(data).encode('hex') == "0100":
      if conn_time > 0.04:
        return False
      return True
    return False
  except socket.error:
    return False

if __name__ == '__main__':

  # generate all the IPs
  for o4 in xrange(2,100):
    servers.append("91.214.237."+str(o4))

  # test servers
  while len(servers) > 0:

    # pick a random server
    server = rndchoice(servers)
    servers.remove(server)

    if testserver(server):
      print server
      try:
        open(str(getenv('HOME'))+"/.gg/cmd","w").write("\
            /set server "+str(server)+"\n\
            /wr\n\
            /reconnect\n\
            /beep\n")
      except:
        continue
      exit(0)
