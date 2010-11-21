#!/usr/bin/python -u

# $Id$

from fcntl import fcntl,F_SETFL
from OpenSSL import SSL
from os import O_NONBLOCK,fork,environ
from select import select
import socket
import sys

#def verifycallback(a1,a2,a3,a4,a5):
#  return 1 

configfile = environ['HOME']+"/.nisroc.rc"

def loadconfig():
  
  global hostdata
  
  hostdata = {}

  try:
    cfg = open(configfile,'r')
  except:
    sys.stderr.write("[-] config file not found - will not check digest\n")

  if cfg:
    for line in cfg.readlines():
      if line[0] != '#':
        line = line.strip()
        val = line.split(';')
        if len(val) == 4:
          hostdata[str(val[0])+":"+str(val[1])] = str(val[2])+";"+str(val[3])


def appconfig(host,port,digest,key):

  try:
    cfg = open(configfile,'a')
    cfg.write(str(host)+";"+str(port)+";"+str(digest)+";"+str(key))
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
  fcntl(0, F_SETFL, O_NONBLOCK)

  s_recv = s.recv
  s_send = s.send
  c_recv = sys.stdin.read
  c_send = sys.stdout.write

  while 1:
    toread,[],[] = select([0,s],[],[],30)
    [],towrite,[] = select([],[1,s],[],30)

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

    ctx = SSL.Context(SSL.SSLv3_METHOD)
    #ctx.set_verify(SSL.VERIFY_NONE,verifycallback)
   
    proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK,1)  
  
    if len(sys.argv) >= 4:
      try:
        proxy.connect((phost,pport))
        proxy.send("CONNECT "+str(host)+":"+str(port)+" HTTP/1.0\r\r")
        data = proxy.recv(128)
        if "200 Connection established" in data:
          sys.stderr.write("[+] connecting to "+str(host)+":"+str(port)+" via proxy "+str(phost)+":"+str(pport)+"\n")
        else:
          sys.stderr.write("[-] problem connecting to "+str(host)+":"+str(port)+" via proxy "+str(phost)+":"+str(pport)+" - maybe not allowed?\n")
          proxy.close()
          sys.exit()

      except socket.error:
        sys.stderr.write("[-] problem connecting to proxy "+str(phost)+":"+str(pport)+"\n")
        proxy.close()
        sys.exit()
    else: 
      try:
        proxy.connect((host,port))
        sys.stderr.write("[+] connecting to "+str(host)+":"+str(port)+"\n")
      except socket.error:
        sys.stderr.write("[-] problem connecting to "+str(host)+":"+str(port)+"\n")
        proxy.close()
        sys.exit()

    ssl = SSL.Connection(ctx,proxy)
    ssl.setblocking(True)
    ssl.set_connect_state()
    ssl.do_handshake()

    sys.stderr.write("[+] ssl handshake done\n")

    if str(host)+":"+str(port) in hostdata:
      digest_save,key = hostdata[str(host)+":"+str(port)].split(';')
    else:
      digest_save = 0
      key = 0

    digest = ssl.get_peer_certificate().digest('sha256')

    if digest_save != 0:
      if digest_save in digest:
        sys.stderr.write("[+] cert digest verified\n")
      else:
        sys.stderr.write("[-] cert digest wrong, possible MITM, exiting\n") 
    else:
      sys.stderr.write("[+] cert digest "+str(digest)+" - not verifed\n")

    if key != 0:
      ssl.send(key)
    elif 'nisroc' in environ:
      ssl.send(environ['nisroc'])
    else:
      sys.stderr.write("[-] no key either in config file or in the evn variable (nisroc) - exiting\n")
      sys.exit()

    data = ssl.recv(1024)
    if data and 'OpenSSH' in data:
      sys.stderr.write("[+] correct key\n")
    else:
      sys.stderr.write("[-] wrong key\n")
      sys.exit()      

    if key == 0:
      appconfig(host,port,digest,environ['nisroc']) 

    sys.stdout.write(data)

    ssl.setblocking(False)

    try:
      exchange(ssl)
    except KeyboardInterrupt:
      pass

    proxy.close()

  else:
    sys.stderr.write("usage: "+sys.argv[0]+" ip_dest port_dest <proxy_ip> <proxy_port>\n")



