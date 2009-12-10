#!/usr/bin/python

import socket

HOST = '10.0.1.1'    # The remote host
PORT = 50007              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send('0123456789876543210')
s.shutdown(socket.SHUT_WR)
data = s.recv(1024)
print 'Received', repr(data)
s.close()
