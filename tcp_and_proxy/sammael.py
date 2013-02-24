#!/usr/bin/python -u

# $Id: 20130224$
# $Date: 2013-02-24 23:46:19$
# $Author: Marek Lukaszuk$

import fcntl
from OpenSSL import SSL
from select import select
from socket import socket,has_ipv6,SHUT_RDWR,AF_INET,AF_INET6,SOCK_STREAM,IPPROTO_TCP,TCP_CORK,SOL_SOCKET,SO_REUSEADDR,error as socket_error
import os
import sys
import pwd
import grp
import time
import random


class sammael():

  def __init__(self,phost="",pport=443,dhost="::1",dport=80):
    self.ver = "20121028"
    self.phost = phost
    self.pport = pport
    self.dhost = dhost
    self.dport = dport
    self.mainpid = os.getpid()

    self.log("sammael ("+str(self.ver)+") - daemon starting")

    if has_ipv6 == True:
      self.s = socket(AF_INET6, SOCK_STREAM)
    else:
      self.s = socket(AF_INET, SOCK_STREAM)

    self.s.setsockopt(IPPROTO_TCP, TCP_CORK, 1)
    self.s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

  def serve(self):
    # starting the server
    self.s.bind((self.phost, self.pport))
    self.s.setblocking(False)
    self.log("bound to socket - "+str(self.phost)+":"+str(self.pport))

    self.deamonsetup()
    self.s.listen(1)
    self.log("listening for connections")
    self.sslctx()

    # main server loop
    while 1:
      accept,[],[] = select([self.s],[],[],60)

      if self.s in accept:
        conn,addr = self.s.accept()

        if os.fork() == 0:
          # this is forked child
          self.chpid = os.getpid()

          data = self.sconn(addr,conn)

          # here we do different things depending on the data recevied
          if data and 'qwerty' in data:
            self.dport = 22

          self.pconn(addr,data)
          self.exchange(addr)
          conn.close()
          sys.exit() # killing the child

      else:
        # cleaning old children
        try:
          os.waitpid(0,os.WNOHANG)
        except OSError:
            pass

  def sslctx(self,prvkey="/usr/local/certs/server.key",pubkey="/usr/local/certs/server.crt",dhfile="/usr/local/cert/dh.dat"):
    # SSL context setup
    self.ctx = SSL.Context(SSL.TLSv1_METHOD)

    self.ctx.use_privatekey_file(prvkey)
    self.ctx.use_certificate_file(pubkey)
    if os.path.isfile(dhfile):
      self.ctx.load_tmp_dh(dhfile)
    self.ctx.set_cipher_list('RC4:-aNULL')

    self.log("SSL context ready")

  def sconn(self,addr,conn):
    # SSL connection initiation
    # conn - socket from the accept call
    # addr - connecting address
    # @data - initial data read

    self.log("new connection from "+str(addr[0])+":"+str(addr[1]))

    # let's add SSL to this socket
    self.ssl = SSL.Connection(self.ctx,conn)
    self.ssl.setblocking(True)
    self.ssl.set_accept_state() # we are SSL server
    time.sleep(random.randint(1000,4000)/1000.0) # random sleep
    self.log(str(self.ssl.state_string()))
    try:
      self.ssl.do_handshake()
    except SSL.Error as e:
      self.log(self.ssl.state_string()+": "+str(e))
      self.ssl.shutdown(SHUT_RDWR)
      conn.shutdown(SHUT_RDWR)
      sys.exit()

    self.log(str(self.ssl.state_string()))

    if not self.ssl.get_servername() == None:
      self.log("client requested servername: "+self.ssl.get_servername())

    try:
      data = self.ssl.recv(1024)
    except:
      self.ssl.shutdown()
      self.log("can't read - connection closed")
      sys.exit()

    self.ssl.setblocking(False)

    return(data)

  def pconn(self,addr,data):
    # Proxy connection initiation
    # addr - connecting address
    # data - initial data read while doing SSL handshake
    self.log("connecting to "+str(self.dhost)+":"+str(self.dport)+" from "+str(addr[0])+":"+str(addr[1]))

    if has_ipv6 == True:
      self.proxy = socket(AF_INET6, SOCK_STREAM)
    else:
      self.proxy = socket(AF_INET, SOCK_STREAM)
    self.proxy.setsockopt(IPPROTO_TCP, TCP_CORK,1)

    try:
      self.proxy.connect((self.dhost, self.dport))
    except socket_error:
      self.ssl.shutdown(SHUT_RDWR)
      self.proxy.shutdown(SHUT_RDWR)
      self.log("problems connecting to "+str(self.dhost)+":"+str(self.dport)+" - connection closed")
      sys.exit()

    self.log("connected to "+str(self.dhost)+":"+str(self.dport)+" from "+str(addr[0])+":"+str(addr[1]))

    #### DEFAULT
    if self.dport == 80: # if we hit the default we need to send the data that we already read from the socket
      self.proxy.send(data)

    fcntl.fcntl(self.proxy, fcntl.F_SETFL, os.O_NONBLOCK)


  def log(self,msg):
    # a more verbose logging
    try:
      print "["+str(self.mainpid)+"->"+str(self.chpid)+"] "+str(msg)
    except:
      print "["+str(self.mainpid)+"] "+str(msg)


  def deamonsetup(self,path="/var/run/sammael/",uid_name='nobody', gid_name='nogroup'):

    if not os.path.exists(path):
      os.makedirs(path)
    os.chdir(path)

    if os.getuid() == 0:
      # We're root, we need to fix that

      # Get the uid/gid from the name
      running_uid = pwd.getpwnam(uid_name).pw_uid
      running_gid = grp.getgrnam(gid_name).gr_gid

      #os.chroot("/var/run/sammael")

      # Try setting the new uid/gid
      os.setgid(running_gid)
      os.setuid(running_uid)

      # Remove group privileges
      #os.setgroups([])

    # Ensure a very conservative umask
    os.umask(077)
    self.log("dropped privs, current ("+str(os.getuid())+"/"+str(os.getgid())+")")

  def exchange(self,addr):
    # main data exchnage function
    # addr - connecting address

    # setting every descriptor to be non blocking
    #fcntl(s, F_SETFL, O_NONBLOCK)
    #s.setblocking(0)
    #fcntl(c, F_SETFL, O_NONBLOCK)

    s_recv = self.ssl.recv
    s_send = self.ssl.sendall
    p_recv = self.proxy.recv
    p_send = self.proxy.send

    self.log("going into exchange between "+str(self.dhost)+":"+str(self.dport)+" and "+str(addr[0])+":"+str(addr[1]))

    while 1:
      toread,[],[] = select([self.proxy,self.ssl],[],[],30)
      [],towrite,[] = select([],[self.proxy,self.ssl],[],30)

      if self.proxy in towrite and self.ssl in toread:
        try:
          data = s_recv(4096)
        except SSL.WantReadError:
          data = ''
        except: #  SSL.SysCallError,SSL.ZeroReturnError:
          break

        ld = len(data)
        if ld > 0:
          p_send(data)

      elif self.proxy in toread and self.ssl in towrite:

        data = p_recv(4096)
        ld = len(data)
        if ld == 0:
          break
        else:
          s_send(data)

    self.proxy.shutdown(SHUT_RDWR)
    self.ssl.sock_shutdown(SHUT_RDWR)
    self.log("connection closed")

# main
if __name__ == "__main__":
  server = sammael()
  server.serve()
