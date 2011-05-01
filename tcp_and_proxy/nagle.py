#!/usr/bin/python -u

# $Id$

from os import O_NONBLOCK,O_NDELAY 
from socket import socket,has_ipv6,AF_INET6,AF_INET,SOCK_STREAM,IPPROTO_TCP,TCP_CORK,error as sock_error
from sys import stdin, stdout, stderr, exit, argv
from select import select
from fcntl import fcntl,F_SETFL

def usage():
  stderr.write("\nusage: "+argv[0]+" <options> host port\n\n\
  version: $Id$\n\n\
  options:\n\
  -w max_waits\n\
   max number of times the timeout value (-t) can be reached before we send the data, default is 5 \n\
  -t seconds\n\
   timeout for a single read (in seconds), default is 0.1\n\
  -s size\n\
   packet size above which we don't buffer, default is 1024 bytes\n\n")
  exit()

# main data exchnage function
def exchange(s,max_waits,timeout,size):
  # input:
  # s - socket object
  # max_waits - max number timeout can be reached
  # timeout - timeout for a single read 
  # size - data size
  # return :
  # nothing :)

  # setting every descriptor to be non blocking 
  fcntl(s, F_SETFL, O_NONBLOCK|O_NDELAY) 
  fcntl(0, F_SETFL, O_NONBLOCK)

  s_recv = s.recv
  s_send = s.send
  write  = stdout.write
  read   = stdin.read  

  more      = 0
  waits     = 0

  while 1:
    toread,[],[] = select([0,s],[],[],timeout)
    [],towrite,[] = select([],[1,s],[],timeout)
    
    if 1 in towrite and s in toread:
      data = s_recv(4096)
      if len(data) == 0:
        s.shutdown(2)
        exit()
      else:
        write(data)

    elif 0 in toread and s in towrite: 
      if more == 0:
        
        ndata = read(4096)
        
#        if len(ndata) == 0:
#          exit()
#        else: 
#          s_send(ndata)
        
        if len(ndata) < size :
          more = 1

      else:
        ndata += read(4096)

      if ndata and len(ndata) >= size or waits >= max_waits: 
        more = 0
        waits = 0
        s_send(ndata)

    elif more == 1:
      waits += 1
      
      if waits >= max_waits:
        more = 0
        waits = 0
        s_send(ndata) 

#### main stuff ####
if __name__ == '__main__':

  if len(argv) >= 3:

    len_argv = len(argv)

    max_waits = 5
    timeout = 0.1
    size = 1024

    try:
      i = 1
      while i<len_argv:

        if argv[i] == '-w':
          max_waits = int(argv[i+1])
          i+=2
        elif argv[i] == '-t':
          timeout = float(argv[i+1])
          i+=2
        elif argv[i] == '-s':
          size = int(argv[i+1])
          i+=2
        else:
          host = argv[i]
          port = int(argv[i+1])
          i+=2

    except:
      usage()

    if ":" in host and has_ipv6 == True:
      s = socket(AF_INET6, SOCK_STREAM)
    else:
      s = socket(AF_INET, SOCK_STREAM)

#    s.setsockopt(IPPROTO_TCP, TCP_CORK,1)

    try:
      s.connect((host, port))
    except sock_error:
      stderr.write("[-] problem connecting to "+str(host)+":"+str(port)+"\n")
      s.close()
      exit()

    try:
      exchange(s,max_waits,timeout,size)
    except KeyboardInterrupt:
      pass      

    s.close()
  
  else:
    usage()
