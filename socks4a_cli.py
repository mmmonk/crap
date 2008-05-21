#!/usr/bin/python

import socket
import struct

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 1080))

host = "212.77.100.101"

host = socket.inet_aton(socket.gethostbyname(host))
data = struct.pack('!BBH',4,1,80)+host+chr(0)

s.send(data);

data = s.recv(1024)

ver,code,head = struct.unpack('BBH',data[:4])
print ' %d %d %d ' % (ver, code, head)

s.close()

