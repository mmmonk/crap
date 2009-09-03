#!/usr/bin/python

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
print "got %s back, TTL %d from target %s" % (res.flags,dttl,dst)

ttldiff=255
for defttl in [64,128,255]:
	tmp=defttl-dttl
	if tmp > 0 and tmp < ttldiff:
		ttldiff=tmp

print "%s is probably %d hops away" % (dst,ttldiff)

my_seq=my_seq+1

data="GET / HTTP/1.0\r"
res=sr1(ip/TCP(sport=my_sport, dport=my_dport, flags="A", seq=my_seq, ack=my_ack)/data,retry=3,timeout=2)

my_ack=res.seq+1
my_seq=my_seq+1

end=0
while end == 0:
	ip.ttl=my_ttl
	back=sr1(ip/TCP(sport=my_sport, dport=my_dport, flags="A", seq=my_seq, ack=my_ack)/data,retry=3,timeout=2)
	if back:	
		#back.display()
		print "%d : %s this hop TTL %d" % (my_ttl,back.src,back.ttl)
		if back.src == dst or my_ttl > 30: 
			print "done: %s" % back.proto
			end=1
	else:
		print "%d : ?????" % my_ttl
	my_ttl=my_ttl+1
