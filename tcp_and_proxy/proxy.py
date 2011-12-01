#!/usr/bin/python -u

version = "20111201"

from fcntl import fcntl, F_SETFL 
from os import O_NONBLOCK
from select import select
from struct import pack,unpack 
import sys
import socket

# use this for a more standard logging mechanism
# import logging

def usage():
  sys.stderr.write("\nusage: "+sys.argv[0]+" <options> proxy_ip proxy_port destination_ip destination_port\n\n\
  version: "+str(version)+"\n\n\
  options:\n\
  -p proxy_type - can be socks4, socks5, http, upnp, default is socks5\n\
  -cork - enables TCP_CORK socket option aka super nagle, default is off\n\n")
  sys.exit(0)

# main data exchnage function
def exchange(s,spawn,s_send,s_recv):

  # setting every descriptor to be non blocking
  fcntl(s, F_SETFL, O_NONBLOCK)
  fcntl(0, F_SETFL, O_NONBLOCK)

  write  = sys.stdout.write
  read   = sys.stdin.read

  while 1:
    toread,[],[] = select([0,s],[],[],60)
    [],towrite,[] = select([],[1,s],[],60)

    if 1 in towrite and s in toread:
      data = s_recv(4096)
      if len(data) == 0:
        s.shutdown(2)
        sys.exit()
      else:
        write(data)

    elif 0 in toread and s in towrite:
      data = read(4096)
      if len(data) == 0:
        sys.exit()
      else:
        s_send(data)

# SOCKS4 or SOCKS4a proxy
def socks4(s,host,port,s_send,s_recv):

  try:
    data = pack('!2BH',4,1,port)+socket.inet_aton(host)+chr(0)
  except socket.error:
    data = pack('!2BH',4,1,port)+socket.inet_aton('0.0.0.1')+chr(0)+host+chr(0)

  s_send(data)
  data = s_recv(256)
  code = unpack('BBH',data[:4])[1]

  if code == 90:
    return 1 
  else:
    return 0 

# SOCKS5 proxy 
def socks5(s,host,port,s_send,s_recv):

  error = ["succeeded", "general SOCKS server failure", "connection not allowed by ruleset", "Network unreachable", "Host unreachable", "Connection refused", "TTL expired", "Command not supported", "Address type not supported", "unassigned"]

  data = pack('!3B',5,1,0)
  s_send(data)
  data = s_recv(256)
  auth = unpack('2B',data)[1]
  if auth != 255:
    nport = pack('!H',port)
    try:
      if ":" in host:
        data = pack('!4B',5,1,0,4)+socket.inet_pton(socket.AF_INET6,host)+nport
      else:
        data = pack('!4B',5,1,0,1)+socket.inet_pton(socket.AF_INET,host)+nport
    except socket.error:
      data = pack('!5B',5,1,0,3,len(host))+host+nport

    s_send(data)
    data = s_recv()
    try:
      code = unpack('BBB',data[:3])[1]
    except:
      sys.stderr.write("[-] socks server sent a wrong replay\n")
      return 0

    if code == 0:
      return 1 
    else:
      if code > 9:
        code=9
      sys.stderr.write("[-] socks server sent an error: "+error[code]+"\n")
      return 0

  else:
    sys.stderr.write("[-] socks server requires authentication\n")
    return 0 

# HTTP CONNECT proxy
def http_connect(s,host,port,s_send,s_recv):

  request = "CONNECT "+str(host)+":"+str(port)+" HTTP/1.0\n\n"
 
  s_send(request)
  data = s_recv(256)
  if "HTTP/1.1 200 " in data or "HTTP/1.0 200 " in data:
    sys.stderr.write("[+] http proxy server allowed the connection\n");
    return 1
  else:
    sys.stderr.write("[-] http proxy server doesn't allow our connection\n"); 
  
  return 0

def upnp(s,host,port):

  data = "<?xml version=\"1.0\"?><s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\"><s:Body><u:AddPortMapping xmlns:u=\"urn:schemas-upnp-org:service:WANIPConnection:1\"><NewRemoteHost></NewRemoteHost><NewExternalPort>31337</NewExternalPort><NewProtocol>TCP</New Protocol><NewInternalPort>"+str(port)+"</NewInternalPort><NewInternalClient>"+str(host)+"</NewInternalClient><NewEnabled>1</NewEnabled><NewPortMappingDescription>proxy</NewPortMappingDescription><NewLeaseDuration>0</NewLeaseDuration></u:AddPortMapping></s:Body></s:Envelope>"

  request = "POST /upnp/control/WANIPConn1 HTTP/1.1\nHost: 172.17.177.129:49000\nUser-Agent: UPnP/1.0\nContent-Length: "+str(len(data))+"\nContent-Type: text/xml\n SOAPAction: \"urn:schemas-upnp-org:service:WANIPConnection:1#AddPortMapping\"\nConnection: Close\nCache-Control: no-cache\nPragma: no-cache\n\n"+str(data)

  s.send(request)

  data = s.recv(256)

  if "HTTP/1.1 200 " in data:
    return 1

  return 0

#### main stuff
if __name__ == '__main__':


  len_argv=len(sys.argv)
  if len_argv >= 5 and len_argv <= 8: 
    
    proxytype = "socks5"
    cork = 0
    spawn = "" 

    try: 
      i = 1
      while i<len_argv:
        if sys.argv[i] == '-p':
          proxytype = sys.argv[i+1]
          i+=2
        elif sys.argv[i] == '-cork':
          cork = 1
          i+=1
        elif sys.argv[i] == '-c':
          spawn = sys.argv[i+1]
          i+=2
        else:
          if spawn == "":
            phost = sys.argv[i]
            pport = int(sys.argv[i+1])
            host  = sys.argv[i+2]
            port  = int(sys.argv[i+3])
            i += 4
          else:
            host  = sys.argv[i]
            port  = int(sys.argv[i+1])
            i += 2

    except:
      usage()
      sys.exit(0);

    proxy = ""


    wr = 0
    rd = 0

    if spawn == "": 

      if ":" in phost and socket.has_ipv6 == True:
        proxy = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
      else:
        proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      
      if cork: 
        proxy.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK,1)

      try:
        proxy.connect((phost, pport))
      except socket.error:
        sys.stderr.write("[-] problem connecting to "+str(phost)+":"+str(pport)+"\n")
        proxy.close()
        sys.exit()  

      sys.stderr.write("[+] connecting via tcp "+str(phost)+":"+str(pport)+" to "+str(host)+":"+str(port)+" proto:"+str(proxytype)+"\n")

      wr = proxy.send
      rd = proxy.recv
    else:
      import subprocess  
     
      sys.stderr.write("[+] connecting using cmd \""+str(spawn)+"\"\n")

      proxy = subprocess.Popen(spawn.split(),stdin=subprocess.PIPE, stdout=subprocess.PIPE,bufsize=0)
  
      sys.stderr.write("[+] connecting using cmd \""+str(spawn)+"\" to "+str(host)+":"+str(port)+" proto:"+str(proxytype)+"\n")

      wr = proxy.stdin.write
      rd = proxy.stdout.readline

    proxyingok = 0 

    if (proxytype == "socks5" and socks5(proxy,host,port,wr,rd)):
      proxyingok = 1 

    if (proxytype == "socks4" and socks4(proxy,host,port,wr,rd)):
      proxyingok = 1 

    if (proxytype == "http" and http_connect(proxy,host,port,wr,rd)):
      proxyingok = 1 
    
    if (proxytype == "upnp" and upnp(proxy,host,port,wr,rd)):
      proxyingok = 1 

    if proxyingok == 1: 
      sys.stderr.write("[+] connection established\n")
      try:
        exchange(proxy,spawn,wr,rd)
      except KeyboardInterrupt: 
        pass
      proxy.close()
    else:
       sys.stderr.write("[-] problem with connecting throught the proxy\n")


  else:
    usage() 
