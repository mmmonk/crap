#!/usr/bin/python

import socket
import time
import os

socket.setdefaulttimeout(5)

hosts_to_watch = [ 'cnn.com', 'wp.pl', 'google.com', 'bbc.co.uk','212.77.100.101','212.58.224.138','209.85.227.99','153.19.42.16'] 
port = 80

logfile = "/root/connection_monitor.log"

WORKDIR = '/'
UMASK = 0
REDIRECT_TO = '/dev/null'

### write log function
def writelog(text):
  log = open(logfile,'a')
  log.write(text)
  log.close()

### main monitoring function
def main_monitor(hosts):

  while 1:
    for host in hosts:
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      try:
        s.connect((host, port))
        s.shutdown(2)
        if hosts_state[host] == 0:
          writelog("%s: connection again possible with connecting to %s\n" % (time.asctime(),host))
          hosts_state[host] = 1
      except socket.error:
        if hosts_state[host] == 1:
          writelog("%s: error connecting to %s\n" % (time.asctime(),host))
          hosts_state[host] = 0
      s.close()
    
    time.sleep(60)


writelog("%s: script started\n" % time.asctime())

hosts_state = {}

for host in hosts_to_watch:
  hosts_state[host] = 1 

try:
  pid = os.fork()
except OSError, e:
  raise Exception, "%s [%d]" % (e.strerror, e.errno)

if pid == 0:
  os.setsid()

  os.chdir(WORKDIR)
  os.umask(UMASK)

  os.close(0)
  os.close(1)
  os.close(2)

  os.open(REDIRECT_TO, os.O_RDWR)
  os.dup2(0, 1)
  os.dup2(0, 2)

  try:
    main_monitor(hosts_to_watch)
  except:
    writelog("%s: script stopped\n" % time.asctime())

else:
  os._exit(0)
