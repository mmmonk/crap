#!/usr/bin/python -u

# $Id$

from fcntl import fcntl, F_SETFL 
from os import O_NONBLOCK
from select import select
from struct import pack,unpack 
import socket
import sys

def usage():
  sys.stderr.write("\nusage: "+sys.argv[0]+" <options> socks_server socks_port destination_ip destination_port\n\n\
  version: $Id$\n\n\
  options:\n\
  -v socks_ver - 4 or 5, default 5\n\
  -cork - enables TCP_CORK socket option aka super nagle, default is off\n\n")
  sys.exit(0)

# main data exchnage function
def exchange(s):
  # input:
  # s - socket object
  # return:
  # nothing :)

  # setting every descriptor to be non blocking
  fcntl(s, F_SETFL, O_NONBLOCK)
  fcntl(0, F_SETFL, O_NONBLOCK)

  s_recv = s.recv
  s_send = s.send
  write  = sys.stdout.write
  read   = sys.stdin.read

  while 1:
    toread,[],[] = select([0,s],[],[],30)
    [],towrite,[] = select([],[1,s],[],30)

    if 1 in towrite and s in toread:
      data = s_recv(4096)
      if len(data) == 0:
        s.shutdown(2)
        sys.exit()
      else:
        write(data)

    elif 0 in toread and s in towrite:
      data = read(4096)
      if len(data) == 0:
        sys.exit()
      else:
        s_send(data)

# preparing a socks4 or socks4a connection
def socks4(s,host,port):
  # input:
  # s - socket object
  # host - destination host either IP or a name
  # port - destination port
  # return:
  # 1 - if ready
  # 0 - if needs authentication 

  try:
    data = pack('!2BH',4,1,port)+socket.inet_aton(host)+chr(0)
  except socket.error:
    data = pack('!2BH',4,1,port)+socket.inet_aton('0.0.0.1')+chr(0)+host+chr(0)

  s.send(data)
  data = s.recv(256)
  code = unpack('BBH',data[:4])[1]

  if code == 90:
    return 1 
  else:
    return 0 

# preaparing a socks5 connection
def socks5(s,host,port):
  # input:
  # s - socket object
  # host - destination host either IP or a name
  # port - destination port
  # return:
  # 1 - if ready
  # 0 - if needs authentication 

  error = ["succeeded", "general SOCKS server failure", "connection not allowed by ruleset", "Network unreachable", "Host unreachable", "Connection refused", "TTL expired", "Command not supported", "Address type not supported", "unassigned"]

  data = pack('!3B',5,1,0)
  s.send(data)
  data = s.recv(1024)
  auth = unpack('2B',data)[1]
  if auth != 255:
    nport = pack('!H',port)
    try:
      if ":" in host:
        data = pack('!4B',5,1,0,4)+socket.inet_pton(socket.AF_INET6,host)+nport
      else:
        data = pack('!4B',5,1,0,1)+socket.inet_pton(socket.AF_INET,host)+nport
    except socket.error:
      data = pack('!5B',5,1,0,3,len(host))+host+nport

    s.send(data)
    data = s.recv(256)
    try:
      code = unpack('BBB',data[:3])[1]
    except:
      sys.stderr.write("[-] socks server sent a wrong replay\n")
      return 0

    if code == 0:
      return 1 
    else:
      if code > 9:
        code=9
      sys.stderr.write("[-] socks server sent an error: "+error[code]+"\n")
      return 0

  else:
    sys.stderr.write("[-] socks server requires authentication\n")
    return 0 

#### main stuff
if __name__ == '__main__':

  len_argv=len(sys.argv)
  if len_argv >= 5 and len_argv <= 8: 
    
    ver = 5
    cork = 0
   
    try: 
      i = 1
      while i<len_argv:
        if sys.argv[i] == '-v':
          ver = sys.argv[i+1]
          i+=2
        elif sys.argv[i] == '-cork':
          cork = 1
          i+=1
        else: 
          phost = sys.argv[i]
          pport = int(sys.argv[i+1])
          host  = sys.argv[i+2]
          port  = int(sys.argv[i+3])
          i+=4
    except:
      usage()
      sys.exit(0);

    if ":" in phost and socket.has_ipv6 == True:
      socks = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
      socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    if cork: 
      socks.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK,1)

    try:
      socks.connect((phost, pport))
    except socket.error:
      sys.stderr.write("[-] problem connecting to "+str(phost)+":"+str(pport)+"\n")
      socks.close()
      sys.exit()  

    sys.stderr.write("[+] connecting via "+str(phost)+":"+str(pport)+" to "+str(host)+":"+str(port)+"\n")

    if (ver == 5 and socks5(socks,host,port)) or (ver == 4 and socks4(socks,host,port)): 
      try:
        exchange(socks)
      except KeyboardInterrupt: 
        pass
      socks.close()
    else:
      sys.stderr.write("[-] socks server couldn't establish the connection\n")

  else:
    usage() 
