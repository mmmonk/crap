#!/usr/bin/python -u

# $Id$

from fcntl import fcntl,F_SETFL
from OpenSSL.SSL import WantReadError as SSL_WantReadError,SysCallError as SSL_SysCallError,ZeroReturnError as SSL_ZeroReturnError,Context as SSL_Context,SSLv3_METHOD,Connection as SSL_Connection
from select import select
from socket import socket,SHUT_RDWR,AF_INET,SOCK_STREAM,IPPROTO_TCP,TCP_CORK,SOL_SOCKET,SO_REUSEADDR,error as socket_error 
from os import chdir,getuid,setgid,setuid,umask,O_NONBLOCK,WNOHANG,fork,waitpid,getpid,getppid
from sys import exit 
import pwd, grp

phost = ''
pport = 443
dhost = '127.0.0.1'
dport = 80
ver = "$Rev$"

def plog(msg, childpid = 0):
  
  if childpid == 0:
    print "["+str(mainpid)+"] "+str(msg)
  else:
    print "["+str(mainpid)+"->"+str(childpid)+"] "+str(msg)


def deamonsetup(uid_name='nobody', gid_name='nogroup'):

#  chroot("/usr/local/certs/")

  chdir("/")

  if getuid() != 0:
    # We're not root so, like, whatever dude
    return

  # Get the uid/gid from the name
  running_uid = pwd.getpwnam(uid_name).pw_uid
  running_gid = grp.getgrnam(gid_name).gr_gid

  # Try setting the new uid/gid
  setgid(running_gid)
  setuid(running_uid)

  # Remove group privileges
  #os.setgroups([])

  # Ensure a very conservative umask
  umask(077)


# main data exchnage function
def exchange(s,c): 
  # input: 
  # s - ssl socket object 
  # c - normal socket object
  # return:
  # nothing :)
  
  # setting every descriptor to be non blocking 
  #fcntl(s, F_SETFL, O_NONBLOCK)
  #s.setblocking(0)
  #fcntl(c, F_SETFL, O_NONBLOCK)
  
  s_recv = s.recv
  s_send = s.sendall
  c_recv = c.recv
  c_send = c.send

  while 1:
    toread,[],[] = select([c,s],[],[],30)
    [],towrite,[] = select([],[c,s],[],30)

    if c in towrite and s in toread:
      try:
        data = s_recv(4096)
      except SSL_WantReadError:
        data = ''
      except SSL_SysCallError,SSL_ZeroReturnError:
        s.sock_shutdown(SHUT_RDWR)
        c.shutdown(SHUT_RDWR)
        break

      if len(data) > 0: 
        c_send(data)

    elif c in toread and s in towrite:

      data = c_recv(4096)
      if len(data) == 0:
        c.shutdown(SHUT_RDWR)
        s.sock_shutdown(SHUT_RDWR)
        break

      else:
        s_send(data)

##### main crap

mainpid = getpid()

plog("sammael ("+str(ver)+") - daemon starting")

s = socket(AF_INET, SOCK_STREAM)
s.setsockopt(IPPROTO_TCP, TCP_CORK, 1)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s.bind((phost, pport))
s.listen(1)

plog("bound to socket - "+str(phost)+":"+str(pport))

deamonsetup()

plog("dropped privs")

### SSL context
ctx = SSL_Context(SSLv3_METHOD)
ctx.use_privatekey_file('/usr/local/certs/server.key')
ctx.use_certificate_file('/usr/local/certs/server.crt')
ctx.set_cipher_list('HIGH')

plog("SSL context ready")
plog("listening for connections")

while (True):
    conn, addr = s.accept()

    try:
      waitpid(0,WNOHANG)
    except OSError:
      pass 
 
    pid = fork()
 
    if pid == 0:

      chpid = getpid()
      # let's add SSL to this socket 
      ssl = SSL_Connection(ctx,conn)
      ssl.setblocking(True)
      ssl.set_accept_state()
      ssl.do_handshake()
      
      data = ssl.recv(1024)

      ssl.setblocking(False)

      if data and 'qwerty' in data:
        dport = 22 
   
      plog("connecting to "+str(dhost)+":"+str(dport)+" from "+str(addr),chpid)
      proxy = socket(AF_INET, SOCK_STREAM)
      proxy.setsockopt(IPPROTO_TCP, TCP_CORK,1)

      try:
        proxy.connect((dhost, dport))
      except socket_error:
        proxy.close()
        conn.close()
        exit()

      plog("connected to "+str(dhost)+":"+str(dport)+" from "+str(addr),chpid)
      
      if dport == 80:
        proxy.send(data)
    
      fcntl(proxy, F_SETFL, O_NONBLOCK)

      plog("going into exchange between "+str(dhost)+":"+str(dport)+" and "+str(addr),chpid)

      exchange(ssl,proxy)
      break

    else:
      plog("child forked "+str(pid))
