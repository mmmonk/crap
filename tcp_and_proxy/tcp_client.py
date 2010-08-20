#!/usr/bin/python

# $Id$

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('www.verisign.com', 443))

ssl_sock = socket.ssl(s)

print repr(ssl_sock.server())
print repr(ssl_sock.issuer())

# Set a simple HTTP request -- use httplib in actual code.
ssl_sock.write("""GET / HTTP/1.0\r
Host: www.verisign.com\r\n\r\n""")

# Read a chunk of data.  Will not necessarily
# read all the data returned by the server.
data = ssl_sock.read()

print data

# Note that you need to close the underlying socket, not the SSL object.
del ssl_sock
s.close()

