#!/usr/bin/python

import socket
import struct

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 1080))

host = "212.77.100.101"
#host = "0.0.0.20"
name = "wp.pl"
port = 80
ver  = 4

a=[ int(i) for i in host.split('.')]

host=socket.inet_aton(host)

data1=struct.pack('!BBH',ver,1,port)+struct.pack('!4H',a[0],a[1],a[2],a[3])+chr(0)+name+chr(0)
data2=struct.pack('!BBH',ver,1,port)+host+chr(0)+name+chr(0)

print "|%s|"%data1
print "|%s|"%data2

s.send(data1);

data = s.recv(1024)

ver,code,head = struct.unpack('BBH',data[:4])
print ' %s %d %s ' % (ver, code, head)

s.send("GET / HTTP\\1.0\r\r")
data = s.recv(1024)

print data

s.close()

