#!/usr/bin/python -u

# $Id$

# based on:
# http://googleonlinesecurity.blogspot.com/2011/04/improving-ssl-certificate-security.html

from OpenSSL.SSL import WantReadError as SSL_WantReadError,SysCallError as SSL_SysCallError,Context as SSL_Context,SSLv23_METHOD,Connection as SSL_Connection
from sys import stdin, stdout, stderr, exit, argv
from socket import socket,has_ipv6,AF_INET,AF_INET6,SOCK_STREAM,IPPROTO_TCP,error as socket_error

version = "$Rev$"

#### main stuff ####
if __name__ == '__main__':

  if len(argv) >= 2:
 
    host = argv[1]
    port = 443
    if len(argv) >= 3:
      port = int(argv[2])
 
    ctx = SSL_Context(SSLv23_METHOD)
    
    if (":" in host and has_ipv6 == True) or (len(argv) >= 4 and ":" in phost and has_ipv6 == True):
      proxy = socket(AF_INET6, SOCK_STREAM)
    else:
      proxy = socket(AF_INET, SOCK_STREAM)
  
    try:
      proxy.connect((host,port))
    except socket_error:
      proxy.close()
      exit("[-] problem connecting to "+str(host)+":"+str(port))

    ssl = SSL_Connection(ctx,proxy)
    ssl.setblocking(True)
    try:
      ssl.set_connect_state()
      ssl.do_handshake()
    except:
      exit(1)

    digest = ssl.get_peer_certificate().digest('sha1')
     
    print digest.replace(":","").lower()+".certs.googlednstest.com"

    proxy.close()

  else:
    stderr.write("usage: "+argv[0]+"\n")



