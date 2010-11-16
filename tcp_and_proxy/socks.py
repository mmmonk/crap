#!/usr/bin/python -u

# $Id$

import os
import socket
import struct
import sys
import select
import fcntl

# main data exchnage function
def exchange(s):
  # input:
  # s - socket object
  # return:
  # nothing :)

  # setting every descriptor to be non blocking
  fcntl.fcntl(s, fcntl.F_SETFL, os.O_NONBLOCK)
  fcntl.fcntl(0, fcntl.F_SETFL, os.O_NONBLOCK)

  s_recv = s.recv
  s_send = s.send
  write  = sys.stdout.write
  read   = sys.stdin.read

  while 1:
    toread,[],[] = select.select([0,s],[],[],30)
    [],towrite,[] = select.select([],[1,s],[],30)

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
    data = struct.pack('!2BH',4,1,port)+socket.inet_aton(host)+chr(0)
  except socket.error:
    data = struct.pack('!2BH',4,1,port)+socket.inet_aton('0.0.0.1')+chr(0)+host+chr(0)

  s.send(data)
  data = s.recv(256)
  code = struct.unpack('BBH',data[:4])[1]

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

  data = struct.pack('!3B',5,1,0)
  s.send(data)
  data = s.recv(1024)
  auth = struct.unpack('2B',data)[1]
  if auth != 255:
    nport = struct.pack('!H',port)
    try:
      data = struct.pack('!4B',5,1,0,1)+socket.inet_aton(host)+nport
    except socket.error:
      data = struct.pack('!5B',5,1,0,3,len(host))+host+nport

    s.send(data)
    data = s.recv(256)
    try:
      code = struct.unpack('BBH',data[:4])[1]
    except:
      return 0

    if code == 0:
      return 1 
    else:
      return 0

  else:
    return 0 

#### main stuff
if __name__ == '__main__':

  if len(sys.argv) >= 5: 
    phost = sys.argv[1]
    pport = int(sys.argv[2])
    host  = sys.argv[3]
    port  = int(sys.argv[4])
    if len(sys.argv) == 6:
      ver = int(sys.argv[5])
    else:
      ver = 5

    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socks.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK,1)

    try:
      socks.connect((phost, pport))
    except socket.error:
      sys.stderr.write("[-] problem connecting to "+str(phost)+":"+str(pport)+"\n")
      socks.close()
      sys.exit()  

    sys.stderr.write("[+] connecting via "+str(phost)+":"+str(pport)+" to "+str(host)+":"+str(port)+"\n")

    if (ver == 5 and socks5(socks,host,port) == 1) or (ver == 4 and socks4(socks,host,port) == 1): 
      exchange(socks)
      socks.close()
    else:
      sys.stderr.write("[-] socks server couldn't establish the connection\n")

  else:
    sys.stderr.write("usage: "+sys.argv[0]+" ip_socks port_socks ip_dest port_dest [socks_ver]\n")
