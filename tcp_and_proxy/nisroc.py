#!/usr/bin/python -u

# $Id: 20130227$
# $Date: 2013-02-27 21:49:40$
# $Author: Marek Lukaszuk$

from OpenSSL import SSL
import fcntl
import os
import select
import sys
from socket import socket,has_ipv6,AF_INET,AF_INET6,SOCK_STREAM,IPPROTO_TCP,TCP_CORK,error as socket_error

configfile = os.environ['HOME']+"/.nisrocrc"
version = "$Rev$"

def loadconfig():

  global hostdata

  hostdata = {}

  try:
    cfg = open(configfile,'r')
  except:
    sys.stderr.write("[-] config file not found - will not check digest\n")
    return

  for line in cfg.readlines():
    if line[0] != '#':
      line = line.strip()
      val = line.split(';')
      sys.stderr.write("[?] data: "+str(val[0])+"-"+str(val[1])+"-"+str(val[2])+"-"+str(val[3])+"\n")
      if len(val) == 4:
        hostdata[str(val[0])+":"+str(val[1])] = str(val[2])+";"+str(val[3])


def appconfig(host,port,digest,key):

  try:
    cfg = open(configfile,'a')
    cfg.write(str(host)+";"+str(port)+";"+str(digest)+";"+str(key)+"\n")
    cfg.close()
  except:
    sys.stderr.write("[-] error adding host to config file\n")

# main data exchnage function
def exchange(s):

  # input:
  # s - socket object
  # c - second socket object
  # return:
  # nothing :)

  # setting every descriptor to be non blocking
  #fcntl(s, F_SETFL, O_NONBLOCK)
  fcntl.fcntl(0, fcntl.F_SETFL, os.O_NONBLOCK)

  s_recv = s.recv
  s_send = s.send
  c_recv = sys.stdin.read
  c_send = sys.stdout.write

  while 1:
    toread,[],[] = select.select([0,s],[],[],30)
    [],towrite,[] = select.select([],[1,s],[],30)

    if 1 in towrite and s in toread:
      try:
        data = s_recv(4096)
      except SSL.WantReadError:
        data = ''
      except SSL.SysCallError:
        s.sock_shutdown(0)
        break

      if len(data) > 0:
        c_send(data)

    elif 0 in toread and s in towrite:

      data = c_recv(4096)

      if len(data) == 0:
        s.sock_shutdown(0)
        break
      else:
        s_send(data)


#### main stuff ####
if __name__ == '__main__':

  if len(sys.argv) >= 3:

    host = sys.argv[1]
    port = int(sys.argv[2])

    if len(sys.argv) >= 4:
      phost = sys.argv[3]
      pport = 8080

    if len(sys.argv) >= 5:
      pport = int(sys.argv[4])

    loadconfig()

    ctx = SSL.Context(SSL.TLSv1_METHOD)

    if (":" in host and has_ipv6 == True) or (len(sys.argv) >= 4 and ":" in phost and has_ipv6 == True):
      proxy = socket(AF_INET6, SOCK_STREAM)
    else:
      proxy = socket(AF_INET, SOCK_STREAM)
    proxy.setsockopt(IPPROTO_TCP, TCP_CORK,1)

    if len(sys.argv) >= 4:

      proxy_str = "CONNECT "+str(host)+":"+str(port)+" HTTP/1.0\r"

      if len(sys.argv) >= 5:
        proxy_str = proxy_str + "Proxy-Authorization: Basic " + str(sys.argv[5]) + "\r"

      try:
        proxy.connect((phost,pport))
        proxy.send(proxy_str+"\r")
        data = proxy.recv(128)
        if "200 Connection established" in data:
          pass
        else:
          proxy.close()
          sys.exit("[-] problem connecting to "+str(host)+":"+str(port)+" via proxy "+str(phost)+":"+str(pport)+" - maybe not allowed?")

      except socket_error:
        proxy.close()
        sys.exit("[-] problem connecting to proxy "+str(phost)+":"+str(pport))
    else:
      try:
        proxy.connect((host,port))
      except socket_error:
        proxy.close()
        sys.exit("[-] problem connecting to "+str(host)+":"+str(port))

    ssl = SSL.Connection(ctx,proxy)
    ssl.setblocking(True)
    try:
      ssl.set_connect_state()
      ssl.do_handshake()
    except:
      sys.exit("[-] ssl handshake error")

    digest_save = 0
    key = 0
    if str(host)+":"+str(port) in hostdata:
      digest_save,key = hostdata[str(host)+":"+str(port)].split(';')

    digest = ssl.get_peer_certificate().digest('sha256')

    if digest_save != 0:
      if digest_save not in digest:
        sys.stderr.write("[-] cert digest wrong, possible MITM, exiting\n")
    else:
      sys.stderr.write("[?] cert digest "+str(digest)+" - not verifed\n")

    if key:
      ssl.send(key)
    elif 'nisroc' in os.environ:
      ssl.send(os.environ['nisroc'])
    else:
      sys.exit("[-] no key either in config file or in the env variable (nisroc) - exiting")

    data = ssl.recv(1024)
    if data and 'OpenSSH' in data:
      sys.stderr.write("[+] connected succesfully - nisroc ("+str(version)+")\n")
    else:
      sys.exit("[-] wrong key")

    if key == 0:
      sys.stderr.write("[+] adding host information to config file "+str(configfile)+"\n")
      appconfig(host,port,digest,os.environ['nisroc'])

    stdout.write(data)

    ssl.setblocking(False)

    try:
      exchange(ssl)
    except KeyboardInterrupt:
      pass

    proxy.close()

  else:
    sys.stderr.write("usage: "+sys.argv[0]+" ip_dest port_dest <proxy_ip> <proxy_port> <base64 encoded string user:pass for proxy auth>\n")



