scapy
=====

* [0trace.py](0trace.py) - a python version of [lcamtuf](http://lcamtuf.coredump.cx/) tool [0trace](http://seclists.org/bugtraq/2007/Jan/176)
* [fork_scan_tcp.py](fork_scan_tcp.py) - a stateless scanning example
* [hsrp_takeover.py](hsrp_takeover.py) - HSRP v1 and v2 takeover
* [hsrp_takeover_research.py](hsrp_takeover_research.py) - HSRP takeover research, probably doesn't work
* [pcap_rewrite.py](pcap_rewrite.py) - very slow and simple pcap rewrite example
* [scan_fw_src_spoof.py](scan_fw_src_spoof.py) - a firewall rules mappers using spoofed source IPs
* [scan_fw_ttl_hlim.py](scan_fw_ttl_hlim.py) - a firewall rules mapper based on ICMP TTL exceeded
* [tcp_session_hijack.py](tcp_session_hijack.py) - a TCP session hijacking example
* [trace.py](trace.py) - traceroute example in scapy
* [vrrp_takeover.py](vrrp_takeover.py) - work in progress

Some short examples
===================

### Usage of Rand functions
    Ether(src=RandMAC())/IP(src=RandIP(),dst="192.168.1.1")/UDP(sport=35)

### DNS query
    IP(dst="172.26.125.105")/UDP(sport=RandShort(),dport=53)/DNS(rd=1,id=RandShort(),qd=DNSQR(qname="monkey.geeks.pl", qtype="AAAA"))

### testing SNMP community strings
    snmpcomm=[comm.strip() for comm in  open("wordlist-common-snmp-community-strings.txt").readlines()]
    send(IP(dst="172.30.72.0/23")/UDP(sport=RandShort(),dport=161)/SNMP(community=snmpcomm,version=["v2c","v1","v2"],PDU=SNMPget(varbindlist=SNMPvarbind(oid="1.3.6.1.2.1.1.1.0"))))

### reading SNMP answers from a pcap file snmp.pcap
    snmp_ans = [p if p.haslayer(SNMPresponse) and p.getlayer(SNMPresponse).error==ASN1_INTEGER(0) else None for p in rdpcap("snmp.pcap")]
    while 1:
     try:
      snmp_ans.remove(None)
     except:
      break

### NTP query against 127.0.0.1
    IP()/UDP()/NTP()

