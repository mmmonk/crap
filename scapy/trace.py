#!/usr/bin/env python
"""
Author: <m.lukaszuk(at)gmail.com> 2009

TCP trace route in scapy :)

to do:
- print what we are rcv at each step
- pretty print some TCP flags
- print only header from the server, remove the rest of the crap


"""

from scapy.all import *
conf.verb=0

import random

my_ttl=1
target=sys.argv[1]
my_dport=80
my_seq=random.randint(1024,65500)
my_sport=my_seq

ip=IP(dst=target)
res=sr1(ip/TCP(sport=my_sport, dport=my_dport, flags="S", seq=my_seq),retry=3,timeout=2)

my_seq=my_seq+1
my_ack=res.seq+1

send(ip/TCP(sport=my_sport, dport=my_dport, flags="A", seq=my_seq, ack=my_ack))

dttl=res.ttl
dst=res.src
print "got %d back, TTL %d from target %s" % (res.flags,dttl,dst)

ttldiff=255
for defttl in [64,128,255]:
	tmp=defttl-dttl
	if tmp > 0 and tmp < ttldiff:
		ttldiff=tmp

print "%s is probably %d hops away (at least one way ;))" % (dst,ttldiff+1)

data="GET / HTTP/1.0\nHost: "+target+"\nUser-Agent: Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\nAccept-Language: en-us,en;q=0.5\n"

res=sr1(ip/TCP(sport=my_sport, dport=my_dport, flags="PA", seq=my_seq, ack=my_ack)/data,retry=3,timeout=2)

my_ack=res.seq
my_seq=my_seq+len(data)

data="Accept-Charset: ISO-8859-2,utf-8;q=0.7,*;q=0.7\nPragma: no-cache\nCache-Control: no-cache\n\n"

end = 0
while end == 0:
	ip.ttl=my_ttl
	rcv = sr1(ip/TCP(sport=my_sport, dport=my_dport, flags="A", seq=my_seq, ack=my_ack)/data,retry=2,timeout=1)
	if rcv:
		print "%d : %s this hop TTL %d" % (my_ttl,rcv.src,rcv.ttl)
		if rcv.proto == 6:
			if rcv.len < 64:
				cap = sniff(filter="tcp and port 80 and port %d" % my_sport, count=1)
				for tmp in cap:
					if tmp.payload.proto == 6 and tmp.payload.len > 128:
						rcv = tmp.payload
							
			print "done, got:\n %s \n" % rcv.payload.payload
#			rcv.display()
			end = 1
		if my_ttl > 30:
			print "out of TTL ;)"
			end = 1
	else:
		print "%d : ?????" % my_ttl
	my_ttl=my_ttl+1
