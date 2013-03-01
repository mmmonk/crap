#!/usr/bin/python -u

# $Id: 20130301$
# $Date: 2013-03-01 13:53:26$
# $Author: Marek Lukaszuk$

from OpenSSL import SSL
from OpenSSL import crypto
from select import select
import fcntl
import socket
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

  def serve(self):
    # starting the server
    self.log("sammael ("+str(self.ver)+") - daemon starting")
    if socket.has_ipv6 == True:
      self.s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
      self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 1)
    self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.s.bind((self.phost, self.pport))
    self.s.setblocking(False)
    self.log("bound to socket - "+str(self.phost)+":"+str(self.pport))

    self.deamonsetup()
    self.sslctx()
    self.s.listen(1)
    self.log("listening for connections")
    self.main_loop()

  def main_loop(self):
    # main server loop
    self.log("entering main accept loop")
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

      # cleaning old children
      try:
        os.waitpid(0,os.WNOHANG)
      except OSError:
          pass

  def sslctx(self,prvkeyfile="/usr/local/certs/server.key",certfile="/usr/local/certs/server.crt",dhfile="/usr/local/certs/dh.dat",ciphers="AES:-MEDIUM:RC4:!aNULL"):
    # SSL context setup
    self.ctx = SSL.Context(SSL.TLSv1_METHOD)

    priv = crypto.load_privatekey(crypto.FILETYPE_PEM,open(prvkeyfile).read())
    priv.check()
    self.log("priv key bits: "+str(priv.bits()))
    self.log("priv key type: "+str(priv.type()))
    cert = crypto.load_certificate(crypto.FILETYPE_PEM,open(certfile).read())
    self.log("cert subject: "+str(cert.get_subject().get_components()))
    self.log("cert notBefore: "+str(cert.get_notBefore()))
    self.log("cert notAfter: "+str(cert.get_notAfter()))
    self.log("cert issuer: "+str(cert.get_issuer().get_components()))
    self.log("cert digest_md5: "+str(cert.digest("md5")))
    self.log("cert digest_sha1: "+str(cert.digest("sha1")))
    if cert.has_expired():
      self.log("cert expired !!!!! - exiting")
      sys.exit()
    self.ctx.use_privatekey(priv)
    self.ctx.use_certificate(cert)
    self.ctx.check_privatekey()
    self.log("certificate and private key loaded correctly")
    if os.path.isfile(dhfile):
      # openssl dHParam -outform PEM -out /usr/local/cert/dh.dat 2048
      self.ctx.load_tmp_dh(dhfile)
      self.log("Ephemeral Diffie-Hellman parameteres loaded correctly from file")
    self.ctx.set_cipher_list(ciphers)
    self.log("cipher suits used are: "+str(ciphers))
    self.log("SSL context ready")

  def CertNamePrint(a):
    return ", ".join([ "=".join(b) for b in a ])

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
      self.ssl.shutdown(2)
      conn.shutdown(2)
      sys.exit()

    self.log(str(self.ssl.state_string()))

    if not self.ssl.get_servername() == None:
      self.log("client requested servername: "+self.ssl.get_servername())

    try:
      data = self.ssl.recv(1024)
    except:
      self.ssl.shutdown(2)
      self.log("can't read - connection closed")
      sys.exit()

    self.ssl.setblocking(False)

    return(data)

  def pconn(self,addr,data):
    # Proxy connection initiation
    # addr - connecting address
    # data - initial data read while doing SSL handshake
    self.log("connecting to "+str(self.dhost)+":"+str(self.dport)+" from "+str(addr[0])+":"+str(addr[1]))

    if socket.has_ipv6 == True:
      self.proxy = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
      self.proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.proxy.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK,1)

    try:
      self.proxy.connect((self.dhost, self.dport))
    except socket.error:
      self.ssl.shutdown(2)
      self.proxy.shutdown(2)
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

    self.log("going into exchange between "+str(self.dhost)+":"+str(self.dport)+" and "+str(addr[0])+":"+str(addr[1]))

    while 1:
      toread,[],[] = select([self.proxy,self.ssl],[],[],30)
      [],towrite,[] = select([],[self.proxy,self.ssl],[],30)

      if self.proxy in towrite and self.ssl in toread:
        try:
          data = self.ssl.recv(4096)
        except SSL.WantReadError:
          data = ''
        except: #  SSL.SysCallError,SSL.ZeroReturnError:
          break

        ld = len(data)
        if ld > 0:
          self.proxy.send(data)

      elif self.proxy in toread and self.ssl in towrite:

        data = self.proxy.recv(4096)
        ld = len(data)
        if ld == 0:
          break
        else:
          self.ssl.sendall(data)

    self.proxy.shutdown(2)
    self.ssl.sock_shutdown(2)
    self.log("connection closed")

# main
if __name__ == "__main__":
  server = sammael()
  server.serve()
