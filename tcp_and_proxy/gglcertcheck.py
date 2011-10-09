#!/usr/bin/python -u

# $Id$

# based on:
# http://googleonlinesecurity.blogspot.com/2011/04/improving-ssl-certificate-security.html

from OpenSSL.SSL import WantReadError as SSL_WantReadError,SysCallError as SSL_SysCallError,Context as SSL_Context,SSLv23_METHOD,Connection as SSL_Connection
from sys import stdin, stdout, stderr, exit, argv
from socket import socket,has_ipv6,AF_INET,AF_INET6,SOCK_STREAM,IPPROTO_TCP,error as socket_error
from dns.resolver import query
from time import localtime,asctime

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
    proxy.close()

    checkcert = digest.replace(":","").lower()+".certs.googlednstest.com"
    try:
      response = query(checkcert,'TXT')
    except:
      exit(0)
    
    if not response:
      print "No response from the DNS for this cert"
      exit(0)

    ans = str(response[0]).replace("\"","").split(" ")
    print asctime(localtime(int(ans[0])*24*3600))
    print asctime(localtime(int(ans[1])*24*3600))
    print ans[2]

  else:
    stderr.write("usage: "+argv[0]+"\n")



