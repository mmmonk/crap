#!/usr/bin/python

import socket
import struct

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 1080))

host = "212.77.100.101"
#host = "wp.pl"
port = 80
ver  = 4 

exit = 0

if ver == 5:
  data = struct.pack('!3B',5,1,0)
  s.send(data)
  data = s.recv(256)
  auth = struct.unpack('2B',data)
  print '%d' % auth
  if auth != 255:
	nport = struct.pack('!H',port)
	try:
	  data = struct.pack('!4B',5,1,0,1)+socket.inet_aton(host)+chr(0)+nport
	except socket.error:
	  data = struct.pack('!5B',5,1,0,3,len(host))+host+nport
  else:
	exit = 1

elif ver == 4:
  try:
	data = struct.pack('!2BH',4,1,port)+socket.inet_aton(host)+chr(0)
  except socket.error:
	data = struct.pack('!2BH',4,1,port)+socket.inet_aton('0.0.0.20')+chr(0)+host+chr(0)

else:
  exit = 1

if exit != 1:
  s.send(data)

  data = s.recv(256)

  ver,code,head = struct.unpack('BBH',data[:4])
  print ' %s %d %s ' % (ver, code, head)

  s.send("GET / HTTP\\1.0\n\n")
  data = s.recv(1024)

  print data

  s.close()

