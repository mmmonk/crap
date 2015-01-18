#!/usr/bin/env python

import socket
import sys
import os

NOTBLOCKED = ["127.0.0.1","::1","0.0.0.0","::"]

def add2hostile(host, times):
    host = "+%s\n" % (host)
    if ":" in host:
        for i in range(times):
            open("/proc/net/xt_recent/www6","w").write(host)
    elif "." in host:
        for i in range(times):
            open("/proc/net/xt_recent/www","w").write(host)

def mainloop(sock):
    while True:
        con, cli = sock.accept()
        try:
            data = con.recv(128)
        finally:
            con.close()
        if data:
            print data
            data = data.split(" ")
            try:
                times = int(data[1])
            except:
                times = 1
            if not data[0] in NOTBLOCKED:
                add2hostile(data[0], times)

def cleanup(location):
    try:
        os.unlink(location)
    except OSError:
        if os.path.exists(location):
            raise

if __name__ == "__main__":
    socket_location = "/tmp/hostile_blocker"

    # Make sure the socket does not already exist
    cleanup(socket_location)

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(socket_location)
    sock.listen(1)
    # 33 is www-data, used by apache
    os.chown(socket_location,33,33)
    # only www-data can write here
    os.chmod(socket_location,0600)

    try:
        mainloop(sock)
    except KeyboardInterrupt:
        sock.close()

    cleanup(socket_location)
