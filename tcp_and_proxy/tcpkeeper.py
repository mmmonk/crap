#!/usr/bin/python -u

# $Id$

from fcntl import fcntl,F_SETFL
from select import select
from socket import socket,has_ipv6,SHUT_RDWR,AF_INET,AF_INET6,SOCK_STREAM,IPPROTO_TCP,SOL_SOCKET,SO_REUSEADDR,error as socket_error 
from os import O_NONBLOCK,WNOHANG,fork,waitpid,getpid,getppid
from sys import argv,exit 

# this is the limit of how many times we try to do a reconnect
# actually the OS also tries to do reconnects, by default it
# will try 3 times per one our try
limit = 10

if len(argv)!=5:
  print "Usage: "+argv[0]+" listening_addr listening_port conn_to_addr conn_to_port"
  exit()

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

try:
  while 1:
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
              # try very hard to send this data ;)
              ok=0
              tries=0
              while ok==0 or tries<=limit: 
                try:
                  out.send(data) 
                  ok=1
                except:
                  pass
                tries+=1
                if ok==0: # if sending fails, lets try to reconnect
                  out = socket(AF_INET, SOCK_STREAM)
                  try:
                    out.connect((dhost, dport))
                  except:
                    pass
              if ok==0:
                plog("could not reconnect in "+str(limit)+" tries",chpid)
                exit()

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
except KeyboardInterrupt:
  plog("Ctrl+C pressed, exiting")
