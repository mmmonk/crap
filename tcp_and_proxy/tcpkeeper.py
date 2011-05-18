#!/usr/bin/python -u

# $Id$

from fcntl import fcntl,F_SETFL
from select import select
from socket import socket,has_ipv6,SHUT_RDWR,AF_INET,AF_INET6,SOCK_STREAM,IPPROTO_TCP,SOL_SOCKET,SO_REUSEADDR,error as socket_error 
from os import O_NONBLOCK,WNOHANG,fork,waitpid,getpid,getppid
from sys import argv,exit 

phost = argv[1]
pport = int(argv[2])
dhost  = argv[3]
dport  = int(argv[4])

def plog(msg, childpid = 0):
  
  if childpid == 0:
    print "["+str(mainpid)+"] "+str(msg)
  else:
    print "["+str(mainpid)+"->"+str(childpid)+"] "+str(msg)

##### main crap

mainpid = getpid()

s = socket(AF_INET, SOCK_STREAM)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s.bind((phost, pport))
s.listen(1)
s.setblocking(False)
plog("bound to socket - "+str(phost)+":"+str(pport))

plog("listening for connections")

while (True):
    accept,[],[] = select([s],[],[],30);

    if s in accept:
      inc,addr = s.accept()

      try:
        waitpid(0,WNOHANG)
      except OSError:
        pass 
   
      pid = fork()
   
      if pid == 0:

        chpid = getpid()
        
        out = socket(AF_INET, SOCK_STREAM)
        try:
          out.connect((dhost, dport))
        except socket_error:
          out.close()
          inc.close()
          exit()

        plog("connected to "+str(dhost)+":"+str(dport)+" from "+str(addr[0])+":"+str(addr[1]),chpid)
        
        fcntl(out, F_SETFL, O_NONBLOCK)

        plog("going into exchange between "+str(dhost)+":"+str(dport)+" and "+str(addr[0])+":"+str(addr[1]),chpid)

        while 1:
          toread,[],[] = select([out,inc],[],[],30)
          [],towrite,[] = select([],[inc],[],30)

          if inc in toread:
            data = inc.recv(4096)
            if len(data) == 0:
              inc.shutdown(SHUT_RDWR)
              break 
            else:
              try:
                out.send(data)
              except:
                plog("reconnecting",chpid);
                out = socket(AF_INET, SOCK_STREAM)
                out.connect((dhost, dport))
                out.send(data)

          elif out in toread:
            data = out.recv(4096)
            if len(data) == 0:
              try:
                out.shutdown(SHUT_RDWR)
              except:
                pass
            else:
              inc.send(data)
        exit()
      else:
        plog("child forked "+str(pid))
