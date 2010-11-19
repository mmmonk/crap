#!/usr/bin/python

# $Id: tcp_half_closed_srv.py 143 2010-08-20 09:15:53Z m.lukaszuk $
from fcntl import fcntl,F_SETFL
from OpenSSL import SSL
from select import select
import socket, sys, os, pwd, grp

phost = ''
pport = 443
dhost = '127.0.0.1'
dport = 80

def deamonsetup(uid_name='nobody', gid_name='nogroup'):

  os.chdir("/")

  if os.getuid() != 0:
    # We're not root so, like, whatever dude
    return

  # Get the uid/gid from the name
  running_uid = pwd.getpwnam(uid_name).pw_uid
  running_gid = grp.getgrnam(gid_name).gr_gid

  # Try setting the new uid/gid
  os.setgid(running_gid)
  os.setuid(running_uid)

  # Remove group privileges
  #os.setgroups([])

  # Ensure a very conservative umask
  old_umask = os.umask(077)


# main data exchnage function
def exchange(s,c): 
  # input: 
  # s - ssl socket object 
  # c - normal socket object
  # return:
  # nothing :)
  
  # setting every descriptor to be non blocking 
  #fcntl(s, F_SETFL, os.O_NONBLOCK)
  #s.setblocking(0)
  #fcntl(c, F_SETFL, os.O_NONBLOCK)
  
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
      except SSL.WantReadError:
        data = ''
      except SSL.SysCallError:
        s.sock_shutdown(socket.SHUT_RDWR)
        c.shutdown(socket.SHUT_RDWR)
        break

      if len(data) > 0: 
        c_send(data)

    elif c in toread and s in towrite:

      data = c_recv(4096)
      if len(data) == 0:
        c.shutdown(socket.SHUT_RDWR)
        s.sock_shutdown(socket.SHUT_RDWR)
        break

      else:
        s_send(data)

##### main crap
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((phost, pport))
s.listen(1)

deamonsetup()

### SSL context
ctx = SSL.Context(SSL.SSLv3_METHOD)
ctx.use_privatekey_file('/usr/local/certs/server.key')
ctx.use_certificate_file('/usr/local/certs/server.crt')
ctx.set_cipher_list('HIGH')

while (True):
    conn, addr = s.accept()

    try:
      os.waitpid(0,os.WNOHANG)
    except OSError:
      pass 
 
    pid = os.fork()
 
    if pid == 0:

      # let's add SSL to this socket 
      ssl = SSL.Connection(ctx,conn)
      ssl.setblocking(True)
      ssl.set_accept_state()
      ssl.do_handshake()
      
      data = ssl.recv(1024)

      ssl.setblocking(False)

      if data and 'qwerty' in data:
        dport = 22 
   
      print "[c] connecting to "+str(dhost)+":"+str(dport)+" from "+str(addr)
      proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      proxy.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK,1)

      try:
        proxy.connect((dhost, dport))
      except socket.error:
        proxy.close()
        conn.close()
        sys.exit()

      print "[c] connected to "+str(dhost)+":"+str(dport)+" from "+str(addr)
      
      if dport == 80:
        proxy.send(data)
    
      fcntl(proxy, F_SETFL, os.O_NONBLOCK)

      print "[c] going into exchange between "+str(dhost)+":"+str(dport)+" and "+str(addr)

      exchange(ssl,proxy)
      break

    else:
      print "[p] Child forked "+str(pid)
