#!/usr/bin/python

import os
import paramiko
import socket
import sys
import threading
import traceback
from select import select

host_key = paramiko.RSAKey(filename="/home/case/host_rsa_key")

ssh_user=""
ssh_pass=""
ssh_key=""

class Server (paramiko.ServerInterface):

  def __init__(self):
    self.event = threading.Event()

  def check_channel_request(self, kind, chanid):
    print "check_channel_request: kind:"+str(kind)+" chanid:"+str(chanid)
    if kind == 'session':
        return paramiko.OPEN_SUCCEEDED
    return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

  def check_auth_password(self, username, password):
    global ssh_user 
    ssh_user = username
    global ssh_pass 
    ssh_pass = password
    return paramiko.AUTH_SUCCESSFUL

  def check_auth_publickey(self, username, key):
    global ssh_key
    ssh_key = key
    return paramiko.AUTH_SUCCESSFUL

  def get_allowed_auths(self, username):
    return 'password' #,publickey'

  def check_channel_shell_request(self, channel):
    self.event.set()
    return True

  def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight ,modes):
    return True


try:
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind(('', 2200))
except Exception, e:
  print '*** Bind failed: ' + str(e)
  traceback.print_exc()
  sys.exit(1)

try:
  sock.listen(100)
  print 'Listening for connection ...'
  client, addr = sock.accept()
except Exception, e:
  print '*** Listen/accept failed: ' + str(e)
  traceback.print_exc()
  sys.exit(1)

try:
  ts = paramiko.Transport(client)
  try:
    ts.load_server_moduli()
  except:
    print '(Failed to load moduli -- gex will be unsupported.)'
    raise
  ts.add_server_key(host_key)
  server = Server()
  try:
    ts.start_server(server=server)
  except paramiko.SSHException, x:
    print '*** SSH negotiation failed.'
    sys.exit(1)

  # wait for auth
  s = ts.accept(20)
  if s is None:
    print '*** No channel.'
    sys.exit(1)
  print 'Authenticated!'

  server.event.wait(10)
  if not server.event.isSet():
    print '*** Client never asked for a shell.'
    sys.exit(1)


  chost = '127.0.0.1'
  cport = 22

  print 'Connecting to the server host/port:'+chost+'/'+str(cport)

  ## Socket connection to remote host
  sockc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sockc.connect((chost, cport))
  
  ## Build a SSH transport
  tc = paramiko.Transport(sockc)
  tc.start_client()
  tc.auth_password(ssh_user,ssh_pass)
  
  c = tc.open_session()
  c.get_pty()
  c.invoke_shell()

  c.settimeout(0.0)
  s.settimeout(0.0)
#  cf = c.fileno()
#  sf = s.fileno()

  while 1:
    toread,[],[] = select([c,s],[],[])
    [],towrite,[] = select([],[c,s],[])

    if c in towrite and s in toread:
      data = s.recv(4096)
      if len(data) == 0:
        s.shutdown(2)
        sys.exit()
      else:
        c.send(data)

    elif c in toread and s in towrite:
      data = c.recv(4096)
      if len(data) == 0:
        sys.exit()
      else:
        s.send(data)

except Exception, e:
  print '*** Caught exception: ' + str(e.__class__) + ': ' + str(e)
  traceback.print_exc()
  try:
    t.close()
  except:
    pass
  sys.exit(1)
 
