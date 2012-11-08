#!/usr/bin/env python

# $Id: 20121108$
# $Date: 2012-11-08 17:05:18$
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

def printcert(cert):
  print "SHA1 digest: " + cert.digest("sha1")
  print "MD5  digest: " + cert.digest("md5")
  print "\ncert details\nissuer: "
  for (a,b) in cert.get_issuer().get_components():
    print "\t"+a+": "+b
  print "pubkey type: "+str(cert.get_pubkey().type())
  print "pubkey bits: "+str(cert.get_pubkey().bits())
  print "serial:      "+str(cert.get_serial_number())
  print "signalgo:    "+str(cert.get_signature_algorithm())
  print "subject:"
  for (a,b) in cert.get_subject().get_components():
    print "\t"+a+": "+b
  print "version:     "+str(cert.get_version())
  print "not before:  "+str(cert.get_notBefore())
  print "not after:   "+str(cert.get_notAfter())

  print "\nextensions:"
  try:
    for i in xrange(0,cert.get_extension_count()-1):
      print cert.get_extension(i)
  except OpenSSL.crypto.Error:
    pass

  print "#"*72

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

  try:
    s.connect((host,443))
  except socket.error:
    print "can't connect"
    sys.exit(1)

  ssl = OpenSSL.SSL.Connection(ctx,s)
  ssl.setblocking(True)

  try:
    ssl.set_connect_state()
    ssl.do_handshake()
    #print ssl.get_cipher_list()
  except:
    exit("[-] ssl handshake error")

  s.shutdown(0)

  peercert = ssl.get_peer_certificate()
  peercertchain = ssl.get_peer_cert_chain()
  digest = peercert.digest('sha1').replace(":","").lower()

  try:
    ans = dns.resolver.query(digest+".notary.icsi.berkeley.edu", 'TXT')
  except:
    ans = False
    print "not found"

  if ans != False:
    v = {}
    for a in str(ans[0]).strip('"').split(" "):
      b = a.split('=')
      v[b[0]] = b[1]
    print "data from http://notary.icsi.berkeley.edu/:"
    print "\tfirst seen:  " + days2ctime(int(v['first_seen']))
    print "\tlast seen:   " + days2ctime(int(v['last_seen']))
    print "\ttimes seen:  " + v['times_seen']
    print "\tvalidated:   " + str(tf(v['validated']))
    print "\n"

  print "peer cert:"
  printcert(peercert)

  print "\n\npeer cert chain:\n"
  for cert in peercertchain:
      printcert(cert)
