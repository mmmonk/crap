#!/usr/bin/python

import socket
import struct
import sys
from threading import Thread


def prd(socket):
  data = 1
  while (data):
    data = socket.recv(1500)
    if data:
      sys.stdout.write(data)

def pwr(socket):
  data = 1
  while(data):
    data = sys.stdin.readline()
    if data:
      socket.send(data)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 1080))

host = sys.argv[1]
port = int(sys.argv[2])
ver  = 5

exit = 0

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
	exit = 1

elif ver == 4 or ver == '4a':
  try:
    data = struct.pack('!2BH',4,1,port)+socket.inet_aton(host)+chr(0)
  except socket.error:
    data = struct.pack('!2BH',4,1,port)+socket.inet_aton('0.0.0.1')+chr(0)+host

else:
  exit = 1

if exit != 1:
  s.send(data)

  data = s.recv(256)

  code = struct.unpack('BBH',data[:4])[1]
  
  if (code == 90 and ver == 4) or (code == 0 and ver == 5): 
    t1 = Thread(target=prd, args=(s,))
    t2 = Thread(target=pwr, args=(s,))

    t1.start()
    t2.start()
  
#    data = 'GET / HTTP/1.0\n\n'
#    s.send(data)
#
#    data = s.recv(1024)
#
#    print data

s.close()

