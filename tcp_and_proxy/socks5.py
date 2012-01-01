#!/usr/bin/python -u

# $Id$

from fcntl import fcntl, F_SETFL 
from os import O_NONBLOCK
from select import select
from struct import pack,unpack 
from time import sleep
import socket
import sys

def usage():
  sys.stderr.write("\nusage: "+sys.argv[0]+" <options> socks_server socks_port destination_ip destination_port\n\n\
  version: $Id$\n\n\
  options:\n\
  -p protocol - tcp/udp/bind (default tcp)\n\
  -cork - enables TCP_CORK socket option aka super nagle, default is off\n\n")
  sys.exit(0)

# preaparing a socks5 connection
def socks5(s,host,port,proto=1):
  # input:
  # s - socket object
  # host - destination host either IP or a name
  # port - destination port
  # return:
  # 1 - if ready
  # 0 - if needs authentication 

  error = ["succeeded", "general SOCKS server failure", "connection not allowed by ruleset", "Network unreachable", "Host unreachable", "Connection refused", "TTL expired", "Command not supported", "Address type not supported", "unassigned"]

  data = pack('!3B',5,1,0)
  s.send(data)
  data = s.recv(2)
  auth = unpack('2B',data)[1]

  if proto == 3: # in UDP we are setting our _source_ address at this stage
    host = "0.0.0.0"
    port = 0

  if auth != 255:
    nport = pack('!H',port)
    try:
      if ":" in host:
        data = pack('!4B',5,proto,0,4)+socket.inet_pton(socket.AF_INET6,host)+nport
      else:
        data = pack('!4B',5,proto,0,1)+socket.inet_pton(socket.AF_INET,host)+nport
    except socket.error:
      data = pack('!5B',5,proto,0,3,len(host))+host+nport

    s.send(data)
    data = s.recv(256)
    dhost = ""
    dport = 0
    try:
      code = unpack('BBBB',data[:4])
      if code[3] == 1:
        dhost = socket.inet_ntop(socket.AF_INET,data[4:8])
        dport = (unpack("!H",data[8:10]))[0]
      elif code[3] == 4:
        dhost = socket.inet_ntop(socket.AF_INET6,data[4:20])
        dport = (unpack("!H",data[20:22]))[0] 
      elif code[3] == 3:
        dhost = data[4:-2]
    except:
      sys.stderr.write("[-] socks server sent a wrong replay\n")
      return (0,0,0) 

    sys.stderr.write("[?] host:"+str(dhost)+" port:"+str(dport)+"\n")
    if code[1] == 0:
      return (code[3],dhost,dport)
    else:
      if code[1] > 9:
        code[1] = 9
      sys.stderr.write("[-] socks server sent an error: "+error[code[1]]+"\n")
      return (0,0,0) 

  else:
    sys.stderr.write("[-] socks server requires authentication\n")
    return (0,0,0) 

#### main stuff
if __name__ == '__main__':

  len_argv=len(sys.argv)
  if len_argv >= 5 and len_argv <= 8: 
    
    ver = 5
    cork = 0
    proto = 1 

    try: 
      i = 1
      while i<len_argv:
        if sys.argv[i] == '-p':
          if sys.argv[i+1] == 'udp':
            proto = 3 
          elif sys.argv[i+1] == 'bind':
            proto = 2 
          else:
            proto = 1 
          i+=2
        elif sys.argv[i] == '-cork':
          cork = 1
          i+=1
        else: 
          phost = sys.argv[i]
          pport = int(sys.argv[i+1])
          host  = sys.argv[i+2]
          port  = int(sys.argv[i+3])
          i+=4
    except:
      usage()
      sys.exit(0);

    if ":" in phost and socket.has_ipv6 == True:
      socks = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
      socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    if cork: 
      socks.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK,1)

    try:
      socks.connect((phost, pport))
    except socket.error:
      sys.stderr.write("[-] problem connecting to "+str(phost)+":"+str(pport)+"\n")
      socks.close()
      sys.exit()  

    sys.stderr.write("[+] connecting via "+str(phost)+":"+str(pport)+" to "+str(host)+":"+str(port)+"\n")

    (atyp,dhost,dport) = socks5(socks,host,port,proto)
    if dhost != 0:
      if proto == 3: # UDP
        print "dhost:"+str(dhost)+" dport:"+str(dport)+"\n"
        
        if atyp == 1:
          udpsocks = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        elif atype == 4: 
          udpsocks = socket.socket(socket.AF_INET6,socket.SOCK_DGRAM)
       
        if ":" in host:
          udpsockshead = pack('!4B',0,0,0,1)+socket.inet_pton(socket.AF_INET6,host)+pack('!H',port)
        else:
          udpsockshead = pack('!4B',0,0,0,1)+socket.inet_pton(socket.AF_INET,host)+pack('!H',port)
        
        udpsocks.sendto(udpsockshead+"hello",(dhost,dport))
        udpsocks.close()
      #sleep(300)
      socks.close()
    else:
      sys.stderr.write("[-] socks server couldn't establish the connection\n")

  else:
    usage() 
