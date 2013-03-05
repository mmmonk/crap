#!/usr/bin/python -u

# $Id: 20130305$
# $Date: 2013-03-05 09:42:43$
# $Author: Marek Lukaszuk$

version = "20111201"

from fcntl import fcntl, F_SETFL
from os import O_NONBLOCK
from select import select
from struct import pack,unpack
from random import randint
import sys
import socket

# use this for a more standard logging mechanism
# import logging

def usage():
  sys.stderr.write("\nusage: "+sys.argv[0]+" <options> proxy_ip proxy_port destination_ip destination_port\n\n\
  version: "+str(version)+"\n\n\
  options:\n\
  -p proxy_type - can be socks4, socks5, http, upnp, default is socks5\n\
  -cork - enables TCP_CORK socket option aka super nagle, default is off\n\n")
  sys.exit(0)


class generic_tcp_proxy:

  def __init__(self,phost,pport,host,port,cork=0):
    self.phost = phost
    self.pport = pport
    self.host = host
    self.port = port
    self.cork = cork

  def init(self):
    if ":" in self.phost and socket.has_ipv6 == True:
      self.proxy = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
      self.proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if self.cork:
      self.proxy.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK,1)

    try:
      self.proxy.connect((self.phost, self.pport))
    except socket.error:
      sys.stderr.write("[-] problem connecting to "+str(self.phost)+":"+str(self.pport)+"\n")
      self.proxy.shutdown()
      sys.exit()

    sys.stderr.write("[+] connecting via tcp "+str(self.phost)+":"+str(self.pport)+" to "+str(self.host)+":"+str(self.port)+"\n")

  def connect(self):
    self.connect = self.proxy

  def send(self,data):
    return self.connect.send(data)

  def recv(self,data):
    return self.connect.recv(data)

  # main data exchange function
  def exchange(self):

    # setting every descriptor to be non blocking
    fcntl(self.connect, F_SETFL, O_NONBLOCK)
    fcntl(0, F_SETFL, O_NONBLOCK)

    write  = sys.stdout.write
    read   = sys.stdin.read

    while 1:
      toread,[],[] = select([0,self.connect],[],[],60)
      [],towrite,[] = select([],[1,self.connect],[],60)

      if 1 in towrite and self.connect in toread:
        data = self.recv(4096)
        if len(data) == 0:
          self.connect.shutdown(2)
          sys.exit()
        else:
          write(data)

      elif 0 in toread and self.connect in towrite:
        data = read(4096)
        if len(data) == 0:
          sys.exit()
        else:
          self.send(data)

# SOCKS4 or SOCKS4a proxy
class socks4 (generic_tcp_proxy):

  def connect(self):

    try:
      data = pack('!2BH',4,1,self.port)+socket.inet_aton(self.host)+chr(0)
    except socket.error:
      data = pack('!2BH',4,1,self.port)+socket.inet_aton('0.0.0.1')+chr(0)+self.host+chr(0)

    self.proxy.send(data)
    data = self.proxy.recv(256)
    code = unpack('BBH',data[:4])[1]

    if code == 90:
      self.connect = self.proxy
      return
    sys.exit(1)

# SOCKS5 proxy
class socks5 (generic_tcp_proxy):

  def connect(self):
    error = ["succeeded", "general SOCKS server failure", "connection not allowed by ruleset", "Network unreachable", "Host unreachable", "Connection refused", "TTL expired", "Command not supported", "Address type not supported", "unassigned"]

    data = pack('!3B',5,1,0)
    self.proxy.send(data)
    data = self.proxy.recv(256)
    auth = unpack('2B',data)[1]
    if auth != 255:
      nport = pack('!H',self.port)
      try:
        if ":" in self.host:
          data = pack('!4B',5,1,0,4)+socket.inet_pton(socket.AF_INET6,self.host)+nport
        else:
          data = pack('!4B',5,1,0,1)+socket.inet_pton(socket.AF_INET,self.host)+nport
      except socket.error:
        data = pack('!5B',5,1,0,3,len(self.host))+self.host+nport

      self.proxy.send(data)
      data = self.proxy.recv(500)
      try:
        code = unpack('BBB',data[:3])[1]
      except:
        sys.stderr.write("[-] socks server sent a wrong replay\n")
        sys.exit(1)

      if code == 0:
        self.connect = self.proxy
        return
      if code > 9:
        code=9
      sys.stderr.write("[-] socks server sent an error: "+error[code]+"\n")
      sys.exit(1)

    else:
      sys.stderr.write("[-] socks server requires authentication\n")
      sys.exit(1)


# HTTP CONNECT proxy
class http_connect (generic_tcp_proxy):

  def connect(self):

    request = "CONNECT "+str(self.host)+":"+str(self.port)+" HTTP/1.1\r\n"

    self.proxy.send(request)
    data = self.proxy.recv(256)
    if "HTTP/1.1 200 " in data or "HTTP/1.0 200 " in data:
      sys.stderr.write("[+] http proxy server allowed the connection\n");
      self.connect = self.proxy
      return

    sys.stderr.write("[-] http proxy server doesn't allow our connection\n");
    sys.exit(1)

# UPNP proxy
class upnp_proxy (generic_tcp_proxy):

  def connect(self):

    jumpport = randint(1025,65535)

    data = "<?xml version=\"1.0\"?><s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\"><s:Body><u:AddPortMapping xmlns:u=\"urn:schemas-upnp-org:service:WANIPConnection:1\"><NewRemoteHost></NewRemoteHost><NewExternalPort>"+str(jumpport)+"</NewExternalPort><NewProtocol>TCP</New Protocol><NewInternalPort>"+str(self.port)+"</NewInternalPort><NewInternalClient>"+str(self.host)+"</NewInternalClient><NewEnabled>1</NewEnabled><NewPortMappingDescription>proxy</NewPortMappingDescription><NewLeaseDuration>0</NewLeaseDuration></u:AddPortMapping></s:Body></s:Envelope>"

    request = "POST /upnp/control/WANIPConn1 HTTP/1.1\nHost: "+str(self.phost)+":"+str(self.pport)+"\nUser-Agent: UPnP/1.0\nContent-Length: "+str(len(data))+"\nContent-Type: text/xml\n SOAPAction: \"urn:schemas-upnp-org:service:WANIPConnection:1#AddPortMapping\"\nConnection: Close\nCache-Control: no-cache\nPragma: no-cache\n\n"+str(data)

    self.proxy.send(request)

    data = self.proxy.recv(256)

    if "HTTP/1.1 200 " in data:
      if ":" in self.phost and socket.has_ipv6 == True:
        self.connect = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
      else:
        self.connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

      if self.cork:
        self.connect.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK,1)

      try:
        self.connect.connect((self.phost, jumpport))
        sys.stderr.write("[+] connecting to "+str(host)+":"+str(port)+" via "+str(self.phost)+":"+str(jumpport)+"\n")

        return
      except socket.error:
        sys.stderr.write("[-] problem connecting to "+str(self.phost)+":"+str(jumpport)+"\n")
        self.connect.shutdown()

    sys.exit(1)

#### main stuff
if __name__ == '__main__':


  len_argv=len(sys.argv)
  if len_argv >= 5 and len_argv <= 8:

    proxytype = "socks5"
    cork = 0
    spawn = ""

    try:
      i = 1
      while i<len_argv:
        if sys.argv[i] == '-p':
          i += 1
          proxytype = sys.argv[i]
        elif sys.argv[i] == '-cork':
          cork = 1
        elif sys.argv[i] == '-c':
          i += 1
          spawn = sys.argv[i]
        else:
          if spawn == "":
            phost = sys.argv[i]
            pport = int(sys.argv[i+1])
            host  = sys.argv[i+2]
            port  = int(sys.argv[i+3])
            i += 3
          else:
            host  = sys.argv[i]
            port  = int(sys.argv[i+1])
            i += 1
          i += 1

    except:
      usage()
      sys.exit(0);

    proxy = socks5(phost,pport,host,port,cork)
    proxy.init()
    proxy.connect()

    sys.stderr.write("[+] connection established\n")
    try:
      proxy.exchange()
    except KeyboardInterrupt:
      pass
    proxy.close()
