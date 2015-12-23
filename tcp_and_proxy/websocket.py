#!/usr/bin/env python

import socket
import sys
from fcntl import fcntl, F_SETFL
from os import O_NONBLOCK
from select import select
from sha import sha
import base64

class WS: # {{{
  """
  a very simple WebSockets client implementation
  https://tools.ietf.org/html/rfc6455
  """

  def __init__(self, target, port=80, path="", proto=[]): # {{{
    """
    initialise some variables
    """
    # TODO add variable for blocking sockets
    self.target = target
    self.port = port
    self.path = path
    self.proto = proto
  # }}}

  def setup(self, bufsize=4096): # {{{
    """
    initial WebSocket connection setup/upgrade
    http://tools.ietf.org/html/rfc6455#section-4
    http://tools.ietf.org/html/rfc6455#section-1.3
    """
    req = "GET /%s HTTP/1.1\r\n" % (self.path) +\
      "Upgrade: websocket\r\n" +\
      "Connection: Upgrade\r\n" +\
      "Host: %s:%s\r\n" % (self.target, self.port) +\
      "Origin: http://%s:%s\r\n" % (self.target, self.port) +\
      "Sec-WebSocket-Key: %s\r\n" % (self.genwskey()) +\
      "Sec-WebSocket-Version: 13\r\n"
    if self.proto:
      req += "Sec-WebSocket-Protocol: %s\r\n" % (", ".join(self.proto))
    req += "\r\n"

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((self.target, self.port))
    s.send(req)
    data = s.recv(bufsize)
    if "Upgrade: websocket" in data and self.vrfywskey(data):
      if self.proto and not vrfyproto(data):
        return False
      self.s = s
      self.s.setblocking(0)
      return True
    return False
  # }}}

  def vrfyproto(self, data): # {{{
    """
    verification of the protocol field
    http://tools.ietf.org/html/rfc6455#section-11.3.4
    http://tools.ietf.org/html/rfc6455#section-1.9
    """
    for line in data.splitlines():
      if "Sec-WebSocket-Protocol:" in line:
        if line.split()[1].strip(", ") in self.proto:
          return True
        else:
          raise(Exception, "reponse protocol doesn't match")

    return True
  # }}}

  def genwskey(self, size=16): # {{{
    """
    generation of the WebSocket key
    """
    self.key = base64.b64encode(open("/dev/urandom").read(size))
    return self.key
  # }}}

  def vrfywskey(self, data): # {{{
    """
    verification of the key
    http://tools.ietf.org/html/rfc6455#section-11.3.1
    """
    for line in data.splitlines():
      if "Sec-WebSocket-Accept:" in line:
        resp = base64.b64decode(line.split()[1].strip())
        expc = sha(self.key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").digest()
        if resp == expc:
          return True
        else:
          raise(Exception, "reponse key doesn't match")

    raise(Exception, "Sec-WebSocket-Accept header not found")
  # }}}

  def wsheader(self, req, fin=True, opcode="text", mask=True): # {{{
    """
    creating websocket request header
    https://tools.ietf.org/html/rfc6455#section-5.2

    """
    if fin:
      out = 0x80
    else:
      out = 0x00

    if opcode == "text":
      out |= 0x01
    elif opcode == "binary":
      out |= 0x10
    else:
      out |= 0x00
    out = chr(out)

    if mask: # masked
      temp = 0x80
    else:
      temp = 0x00

    extpll = ""
    if len(req) < 126:
      temp |= len(req)
    elif len(req) < 65536:
      temp |= 0x7e
      extpll = struct.pack("!H",len(req))
    else:
      temp |= 0x7f
      extpll = struct.pack("!Q",len(req))

    out += chr(temp)
    if extpll:
      out += chr(extpll)
    return out
  # }}}

  def wsget(self, bufsize=4096): # {{{
    """
    parsing the websocket headers here
    this is done in a veeeeeery simple way
    this might produce wrong results
    http://tools.ietf.org/html/rfc6455#section-6.2
    """
    out = ""
    data = self.s.recv(bufsize)
    restarted = False
    if len(data) == 0:
      self.setup()
      restarted = True
    else:
      while len(data) > 2:
        startidx = 2
        dlen = ord(data[1]) & 0x7f # length of response
        masked = ord(data[1]) & 0x80 == 0x80 # masked ?
        if dlen == 126:
          startidx += 2
          dlen = struct.unpack("!H",data[startidx-2:startidx])[0]
        elif dlen == 127:
          startidx += 8
          dlen = struct.unpack("!Q",data[startidx-8:startidx])[0]
        if masked:
          startidx += 4
          key = data[startidx-4:startidx]
          out += "%s\n" % (self.masking(key, data[startidx:startidx+dlen]))
        else:
          out += "%s\n" % (data[startidx:startidx+dlen])
        data = data[startidx+dlen:]
    return out, restarted
  # }}}

  def wssend(self, data, mask=False): # {{{
    """
    sending a websocket request
    http://tools.ietf.org/html/rfc6455#section-6.1
    """
    if mask:
      key = open("/dev/urandom").read(4)
      out = key+self.masking(key, data)
    else:
      out = data
    self.s.send(self.wsheader(data, mask=mask) + out)
  # }}}

  def masking(self, key, data): # {{{
    """
    function for masking input (XORing)
    """
    key = map(ord, key) # we just need the values
    keys = len(key) # size of the key
    return "".join([chr(ord(data[i]) ^ key[i%keys]) for i in range(len(data))])
  # }}}

  def comm(self, fdrd=sys.stdin, fdwr=sys.stdout, bufsize=4096): # {{{
    """
    main communication - example usage
    """
    if not self.setup():
      raise(Exception, "connection to %s can't be established" % (self.target))

    fcntl(fdrd, F_SETFL, O_NONBLOCK)

    while True:
      toread,[],[] = select([fdrd,self.s],[],[],60)
      [],towrite,[] = select([],[fdwr,self.s],[],60)

      if fdwr in towrite and self.s in toread:
        fdwr.write(self.wsget()[0])

      elif fdrd in toread and self.s in towrite:
        data = fdrd.read(bufsize)
        self.wssend(data)
  # }}}
# }}}

if__name__ == "__main__":

  if len(sys.argv) < 4:
    print "usage: %s target port path" % (sys.argv[0])
    sys.exit(1)

  target = sys.argv[1]
  port = int(sys.argv[2])
  path = sys.argv[3]

  a = WS(target, port, path)
  try:
    a.comm()
  except KeyboardInterrupt:
    print "\nCtrl+C pressed exiting"
