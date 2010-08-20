#!/usr/bin/env python

# $Id$
"""
Author: <m.lukaszuk(at)gmail.com> 2009

TCP trace route using scapy :)

"""

from scapy.all import conf,IP,TCP,sr1,sniff,send
conf.verb = 0

import random
import re
import sys

my_ttl = 1
target = sys.argv[1]
my_dport = 80
my_seq = random.randint(1024,65500)
my_sport = my_seq

def dec2bin(a,b):
  '''
  and the question is why it took until release 2.6 of python to realize that
  some people actually use binary numbers
  '''
  if a == 0:
	return 0
  else:
	b.append(a % 2)
	dec2bin((int)(a / 2),b)

def TCPflags(a):
  '''
  prints TCP flags in a nice way
  '''
  flags = ['F','S','R','P','A','U','E','C']
  tcpflags = []
  dec2bin(a,tcpflags)

  retval=""

  i = 0
  for val in tcpflags:
	if val == 1:
	  retval = retval+flags[i]
	i = i+1

  return retval 


ip = IP(dst = target)
res = sr1(ip/TCP(sport = my_sport, dport = my_dport, flags = "S", seq = my_seq),retry = 3,timeout = 2)

my_seq = my_seq+1
my_ack = res.seq+1

send(ip/TCP(sport = my_sport, dport = my_dport, flags = "A", seq = my_seq, ack = my_ack))

dttl = res.ttl
dst = res.src
print "got back TCP flags %s and TTL %d from target %s" % (TCPflags(res.payload.flags),dttl,dst)

ttldiff = 255
for defttl in [64,128,255]:
  tmp = defttl-dttl
  if tmp > 0 and tmp < ttldiff:
	ttldiff = tmp

print "%s is probably %d hops away (at least one way ;))" % (dst,ttldiff+1)

data = "GET / HTTP/1.0\nHost: "+target+"\nUser-Agent: Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2\nAccept: text/html,application/xhtml+xml,application/xml;q = 0.9,*/*;q = 0.8\nAccept-Language: en-us,en;q = 0.5\n"

res = sr1(ip/TCP(sport = my_sport, dport = my_dport, flags = "PA", seq = my_seq, ack = my_ack)/data,retry = 3,timeout = 2)

my_ack = res.seq
my_seq = my_seq+len(data)

data = "Accept-Charset: ISO-8859-2,utf-8;q = 0.7,*;q = 0.7\nPragma: no-cache\nCache-Control: no-cache\n\n"

while 1 == 1:
  ip.ttl = my_ttl
  rcv = sr1(ip/TCP(sport = my_sport, dport = my_dport, flags = "A", seq = my_seq, ack = my_ack)/data,retry = 2,timeout = 1)
  if rcv:
	print "%2d : %15s rcv proto %s, TTL %3d" % (my_ttl,rcv.src,rcv.proto,rcv.ttl)

	if rcv.proto == 6:
	  if dttl != rcv.ttl:
		print "Probable SYN proxy, SA TTL %d, now TTL %d" % (dttl,rcv.ttl)
	  print "done, got: TCP flags: %s" % TCPflags(rcv.payload.flags)

	  if len(rcv.payload.payload) < 10: 
		cap = sniff(filter = "tcp and port 80 and port %d and host %s" % (my_sport,dst), count = 1,timeout = 5)
		for tmp in cap:
		  if tmp.payload.proto == 6 and len(tmp.payload.payload.payload) < 10:
			rcv = tmp.payload
			break

	  if rcv.len > 128:
		header = str(rcv.payload.payload)
		header = (re.split('\n\s*\n',header,2))[0]
		print "\n%s" % header
#	  rcv.display()
	  break	

	if my_ttl > 25:
	  print "out of TTL ;)"
	  break
  else:
	print "%2d : ???.???.???.???" % my_ttl
  my_ttl = my_ttl+1
