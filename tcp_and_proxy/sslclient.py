#!/usr/bin/python

# $Id$

from OpenSSL import SSL
import socket

fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
fd.connect(('profil.wp.pl',443))

ctx = SSL.Context(SSL.SSLv3_METHOD)
#ctx.set_verify(VERIFY_NONE) 

ssl = SSL.Connection(ctx,fd) 
ssl.set_connect_state()
ssl.do_handshake()

print ssl.get_peer_certificate().digest('sha256')

TEST = "HEAD /\nUser-Agent: ThisIsTypicalBrowserPleaseIgnore\n\n"

ssl.send(TEST)

print ssl.recv(4096)

fd.close()
