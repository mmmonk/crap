#!/usr/bin/python -u

# $Id$

import os
import socket
import sys
import select
import fcntl

# main data exchnage function
def exchange(s):
  # input:
  # s - socket object
  # return:
  # nothing :)

  # setting every descriptor to be non blocking 
  fcntl.fcntl(s, fcntl.F_SETFL, os.O_NONBLOCK|os.O_NDELAY) 
  fcntl.fcntl(0, fcntl.F_SETFL, os.O_NONBLOCK)

  s_recv = s.recv
  s_send = s.send
  write  = sys.stdout.write
  read   = sys.stdin.read  
  nagle  = 0
  n_c    = 0
  n_l    = 5    # how many timeout do we wait for
  n_tout = 0.1  # actual max wait is n_tout*n_l 
  n_size = 1024 # minimum size of the packet 

  while 1:
    toread,[],[] = select.select([0,s],[],[],n_tout)
    [],towrite,[] = select.select([],[1,s],[],n_tout)
    
    if 1 in towrite and s in toread:
      data0 = s_recv(4096)
      if len(data0) == 0:
        s.shutdown(2)
        break
      else:
        write(data0)

    elif 0 in toread and s in towrite: 
      # if we are not waiting for any data then just
      # overwrite the buffer
      if nagle == 0:
        data1 = read(4096)

        # conditions for buffering data
        if len(data1) < n_size:
          nagle = 1

      else:
        # if we are waiting then add to the existing buffer
        data1 += read(4096)
        # n_c += 1 # <- this is not needed here

      # this is reach when the data has enough size
      if data1 and (len(data1) >= n_size or n_c >= n_l):
        nagle = 0
        n_c = 0
        s_send(data1)

    elif nagle == 1:
      n_c += 1

      # this is reached when we timeout waiting 
      # for the data
      if n_c >= n_l:
        nagle = 0
        n_c = 0
        s_send(data1)

#### main stuff ####
if __name__ == '__main__':

  if len(sys.argv) >= 2: 
    host = sys.argv[1]
    port = int(sys.argv[2])

    nagle = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
      nagle.connect((host, port))
    except socket.error:
      sys.stderr.write("[-] problem connecting to "+str(host)+":"+str(port)+"\n")
      nagle.close()
      sys.exit()  

    try:
      exchange(nagle)
    except KeyboardInterrupt:
      pass      

    nagle.close()
  
  else:
    sys.stderr.write("usage: "+sys.argv[0]+" ip_dest port_dest\n")
