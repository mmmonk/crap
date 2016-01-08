#!/usr/bin/env python

import sys

"""
a very simple cli hex file editor
"""

if len(sys.argv) < 3:
  sys.stderr.write("usage: %s file hex_offset <hex_value>\n" % (sys.argv[0]))
  sys.exit(0)

def hprint(fd, off, size):
  fd.seek(off)
  sys.stdout.write("offset:0x%x %s\n" % (off, fd.read(size).encode('hex')))

try:
  size = 1
  off = int(sys.argv[2], 16)
except ValueError:
  size = int(sys.argv[2].split("-")[1])
  off = int(sys.argv[2].split("-")[0], 16)

fd = open(sys.argv[1],"rw+")
if len(sys.argv) > 3:
  data = sys.argv[3].decode('hex')
  size = len(data) if size < len(data) else size
  hprint(fd, off, size)
  fd.seek(off)
  fd.write(data)
hprint(fd, off, size)
fd.close()
