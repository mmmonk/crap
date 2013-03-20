#!/usr/bin/python -u

# $Id: 20130320$
# $Date: 2013-03-20 07:13:06$
# $Author: Marek Lukaszuk$

from OpenSSL import SSL
import fcntl
import os
import select
import sys
import socket
import argparse

version = "20130228"

class nisroc():

  def __init__(self,configfile="~/.nisrocrc",host="",port=0 ,phost="",pport=8080 ,auth="", dontcheckdigest=False, srvpass=""):

    self.host = host
    self.port = port
    self.phost = phost
    self.pport = pport
    self.auth = auth
    self.srvpass = srvpass
    self.configfile = os.path.abspath(os.path.expanduser(configfile))
    self.hostdata = dict()

    try:
      cfg = open(self.configfile,'r')
    except:
      self.log("config file not found - will not check digest",bad=1)
      if not dontcheckdigest:
        sys.exit()
      if self.srvpass == "":
        sys.exit()


    if os.path.isfile(self.configfile):
      for line in cfg.readlines():
        if line[0] != '#':
          val = line.strip().split(';')
          self.log("data: "+str(val[0])+"-"+str(val[1])+"-"+str(val[2])+"-"+str(val[3]))
          if len(val) == 4:
            hostdata[str(val[0])+":"+str(val[1])] = str(val[2])+";"+str(val[3])

      cfg.close()

    # SSL context
    self.ctx = SSL.Context(SSL.TLSv1_METHOD)
    self.ctx.set_cipher_list('RC4')

    if (socket.has_ipv6 == True and (":" in self.host or ":" in self.phost)):
      self.conn = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
      self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK,1)

  def connect(self):
    if not self.phost == "":
      self.httpproxy()
    else:
      self.normalcon()

    try:
      self.handshake()
      self.exchange()
      self.conn.shutdown(2)
    except KeyboardInterrupt:
      pass


  def appconfig(self,host,port,digest,key):
    # adding new cert to the config
    try:
      open(self.configfile,'a').write(str(host)+";"+str(port)+";"+str(digest)+";"+str(key)+"\n")
    except:
      self.log("error adding host to config file",bad=1)

  def log(self,msg,bad=0):
    # logging
    if bad == 0:
      sign = "+"
    else:
      sign = "-"
    sys.stderr.write("["+str(sign)+"] "+str(msg)+"\n")

  def exchange(self):
    # main data exchange function

    # stdout non blocking
    fcntl.fcntl(0, fcntl.F_SETFL, os.O_NONBLOCK)

    while 1:
      toread,[],[] = select.select([0,self.ssl],[],[],30)
      [],towrite,[] = select.select([],[1,self.ssl],[],30)

      if 1 in towrite and self.ssl in toread:
        try:
          data = self.ssl.recv(4096)
        except SSL.WantReadError:
          data = ''
        except:
          break

        if len(data) > 0:
          sys.stdout.write(data)

      elif 0 in toread and self.ssl in towrite:

        data = sys.stdin.read(4096)

        if len(data) == 0:
          break
        else:
          self.ssl.send(data)

    self.ssl.shutdown(2)

  def httpproxy(self):

    proxy_str = "CONNECT "+str(self.host)+":"+str(self.port)+" HTTP/1.0\r"

    if not self.auth == "":
      proxy_str = proxy_str + "Proxy-Authorization: Basic " + str(self.auth) + "\r"

    try:
      self.conn.connect((self.phost,self.pport))
      self.conn.send(proxy_str+"\r")
      data = self.conn.recv(128)
      if "200 Connection established" in data:
        pass
      else:
        self.conn.shutdown(2)
        self.log("problem connecting to "+str(self.host)+":"+str(self.port)+" via proxy "+str(self.phost)+":"+str(self.pport)+" - maybe not allowed?",bad=1)
        sys.exit()
    except socket.error:
      self.conn.shutdown(2)
      sys.log("problem connecting to proxy "+str(self.phost)+":"+str(self.pport),bad=1)
      sys.exit()


  def normalcon(self):

    try:
      self.conn.connect((self.host,self.port))
    except socket.error:
      self.log("problem connecting to "+str(self.host)+":"+str(self.port),bad=1)
      sys.exit()


  def handshake(self):

    self.ssl = SSL.Connection(self.ctx,self.conn)
    self.ssl.setblocking(True)
    try:
      self.ssl.set_connect_state()
      self.ssl.do_handshake()
    except:
      self.log("ssl handshake error",bad=1)
      sys.exit()

    digest_save = ""
    key = ""
    if str(self.host)+":"+str(self.port) in self.hostdata:
      digest_save,key = self.hostdata[str(self.host)+":"+str(self.port)].split(';')

    digest = self.ssl.get_peer_certificate().digest('sha1')

    if digest_save != "":
      if digest_save != digest:
        self.log("cert digest wrong, possible MITM",bad=1)
        sys.exit()
    else:
      self.log("cert digest "+str(digest)+" - not verifed")

    if key:
      self.ssl.send(key)
    elif not self.srvpass == "":
      self.ssl.send(self.srvpass)
    else:
      self.log("no key either in config file or in the env variable (nisroc) - exiting",bad=1)
      sys.exit()

    data = self.ssl.recv(1024)
    if data and 'OpenSSH' in data:
      self.log("connected succesfully - nisroc ("+str(version)+")")
    else:
      self.log("wrong key",bad=1)
      sys.exit()

    if key == 0:
      self.log("adding host information to config file "+str(configfile))
      appconfig(host,port,digest,os.environ['nisroc'])

    sys.stdout.write(data)

    self.ssl.setblocking(False)


#### main stuff ####
if __name__ == '__main__':

  p = argparse.ArgumentParser()
  p.add_argument("host", help="destination host")
  p.add_argument("port", type=int, help="destination port")
  p.add_argument("-ph", default="", help="http proxy host")
  p.add_argument("-pp", type=int, default=8080, help="http proxy port (default: 8080)")
  p.add_argument("-auth", default="", help="base64 encoded string user:pass for basic proxy auth")
  p.add_argument("-pwd", default="", help="the pass string to connect to the \"hidden\" service")
  p.add_argument("-dc", action='store_true', help="don't check server digest with the local file (it will still be stored if it is not there)")

  args = p.parse_args()

  c = nisroc(host=args.host, port=args.port, phost=args.ph, pport=args.pp, auth=args.auth, dontcheckdigest=args.dc, srvpass=args.pwd)
  c.connect()
