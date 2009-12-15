#!/usr/bin/python -u

import os
import socket
import sys
import select
import fcntl


def xor(xorstr,xorsec,i,xorseclen):
  # input:
  # xorstr - data
  # xorsec - xoring secret
  # i - where are we in the xoring secret
  # xorseclen - the length of xoring secret
  # return:
  # i - where did we finish in the xoring secret
  # s - xorred data

  xorstr = map (ord, xorstr)
  xorstrrange = range(len(xorstr))

  for c in xorstrrange:
    xorstr[c]=(xorstr[c]^xorsec[i])
    i+=1
    if i >= xorseclen:
      i = 0

  s = ""
  return i,s.join(map(chr, xorstr))


# main data exchange function
def exchange(s):
  # input:
  # s - socket object
  # return:
  # nothing :)

  # setting every description to be non blocking 
  fcntl.fcntl(s, fcntl.F_SETFL, os.O_NONBLOCK|os.O_NDELAY) 
  fcntl.fcntl(0, fcntl.F_SETFL, os.O_NONBLOCK)

  secret = map(ord,"testowysecret")
  secretlen = len(secret)
  secreti = 0
  secreto = 0

  while 1:
    toread,towrite,[]=select.select([sys.stdin,s],[s],[],30)
    
    if s in toread:
      data = s.recv(1500)
      secreti,data = xor(data,secret,secreti,secretlen)
      if len(data) == 0:
        s.shutdown(2)
        break
      else:
        sys.stdout.write(data)
    if sys.stdin in toread and s in towrite:
      data = sys.stdin.read(1500)
      secreto,data = xor(data,secret,secreto,secretlen)
      if data:
          s.send(data)

#### main stuff
if __name__ == '__main__':

  if len(sys.argv) >= 2: 
    host = sys.argv[1]
    port = int(sys.argv[2])

    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
      socks.bind((host, port))
    except socket.error:
      sys.stderr.write("[-] problem with binding to "+str(host)+":"+str(port)+"\n")
      socks.close()
      sys.exit()  

    socks.listen(1)
    conn, addr = socks.accept()
    sys.stderr.write("[+] connection accepted from "+str(addr[0])+":"+str(addr[1])+"\n")
    exchange(conn)
    conn.close()
  else:
    sys.stderr.write("usage: "+sys.argv[0]+" bind_ip bind_port\n")
