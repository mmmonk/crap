#!/usr/bin/env python

# $Id: 20121104$
# $Date: 2012-11-04 21:53:05$
# $Author: Marek Lukaszuk$
#
# this is based on http://notary.icsi.berkeley.edu/

import OpenSSL.SSL
import socket
import sys
import dns.resolver
import time

def days2ctime(days):
  return time.strftime("%Y-%m-%d",time.localtime(days * 86400))

def tf(val):
  if int(val) == 1:
    return True
  return False

if __name__  == "__main__":
  try:
    host = sys.argv[1]
  except:
    sys.exit(1)

  ctx = OpenSSL.SSL.Context(OpenSSL.SSL.TLSv1_METHOD)

  if ":" in host and socket.has_ipv6 == True:
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
  else:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK,1)

  s.connect((host,443))

  ssl = OpenSSL.SSL.Connection(ctx,s)
  ssl.setblocking(True)

  try:
    ssl.set_connect_state()
    ssl.do_handshake()
  except:
    exit("[-] ssl handshake error")

  digest = ssl.get_peer_certificate().digest('sha1')
  digest = digest.replace(":","").lower()
  try:
    ans = dns.resolver.query(digest+".notary.icsi.berkeley.edu", 'TXT')
  except:
    print "not found"
    sys.exit(1)

  v = {}
  for a in str(ans[0]).strip('"').split(" "):
    b = a.split('=')
    v[b[0]] = b[1]

  print "sha1 digest:" + digest
  print "first seen: " + days2ctime(int(v['first_seen']))
  print "last seen:  " + days2ctime(int(v['last_seen']))
  print "times seen: " + v['times_seen']
  print "validated:  " + str(tf(v['validated']))
  s.shutdown(0)
