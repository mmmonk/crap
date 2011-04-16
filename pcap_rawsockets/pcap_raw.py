#!/usr/bin/python

# $Id$

import pcap
import sys
import string
import struct
from socket import *

proto = 0x55aa

s = socket(AF_PACKET, SOCK_RAW, proto)
s.bind(("wlan0",proto))

ifName,ifProto,pktType,hwType,hwAddr = s.getsockname()

srcAddr = hwAddr
dstAddr = "\x01\x02\x03\x04\x05\x06"
ethData = "here is some data for an ethernet packet"

txFrame = struct.pack("!6s6sh",dstAddr,srcAddr,proto) + ethData

print "Tx[%d]: "%len(ethData) + string.join(["%02x"%ord(b) for b in
ethData]," ")

s.send(txFrame)

rxFrame = s.recv(2048)

dstAddr,srcAddr,proto = struct.unpack("!6s6sh",rxFrame[:14])
ethData = rxFrame[14:]

print "Rx[%d]: "%len(ethData) + string.join(["%02x"%ord(b) for b in
ethData]," ")

s.close()

