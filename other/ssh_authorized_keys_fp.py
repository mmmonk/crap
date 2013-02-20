#!/usr/bin/env python

# $Id: 20130220$
# $Date: 2013-02-20 15:49:35$
# $Author: Marek Lukaszuk$

import argparse
import glob
import os
import tempfile
from subprocess import check_output

p = argparse.ArgumentParser(description='get the fingerprints for multiple ssh public keys')
p.add_argument("-f",help="a file to analyse, may use global patterns, by default: /home/*/.ssh/authorized_keys", default="/home/*/.ssh/authorized_keys")
args = p.parse_args()

for f in glob.glob(args.f):
  for l in open(f).readlines():
    t = tempfile.NamedTemporaryFile(delete=False)
    t.write(l)
    t.flush()
    o = check_output(["ssh-keygen","-l","-f",t.name])
    t.close()
    os.unlink(t.name)
    print str(f)+" "+str(o),
