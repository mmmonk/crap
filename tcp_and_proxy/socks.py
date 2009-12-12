#!/usr/bin/python -u

import os
import socket
import struct
import sys
import select
import fcntl

phost = sys.argv[1]
pport = int(sys.argv[2])
host  = sys.argv[3]
port  = int(sys.argv[4])
ver   = 5

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((phost, pport))

if ver == 5:
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
  else:
    sys.exit()

elif ver == 4 or ver == '4a':
  try:
    data = struct.pack('!2BH',4,1,port)+socket.inet_aton(host)+chr(0)
  except socket.error:
    data = struct.pack('!2BH',4,1,port)+socket.inet_aton('0.0.0.1')+chr(0)+host+chr(0)

else:
  sys.exit()

s.send(data)
data = s.recv(256)
code = struct.unpack('BBH',data[:4])[1]

if (code == 90 and ver == 4) or (code == 0 and ver == 5): 

  fcntl.fcntl(s, fcntl.F_SETFL, os.O_NONBLOCK|os.O_NDELAY) 
  fcntl.fcntl(0, fcntl.F_SETFL, os.O_NONBLOCK)

  while 1:
    toread,[],[]=select.select([sys.stdin,s],[],[],30)
    
    if s in toread:
      data = s.recv(1500)
      if data:
          sys.stdout.write(data)
    if sys.stdin in toread:
      data = sys.stdin.read(1500)
      if data:
          s.send(data)

s.close()
