#!/usr/bin/env python

from __future__ import print_function

import subprocess
import shlex
import time
import random
import os
import sys

REFRESH_LIMIT_HOURS = 7*24
HTTP_PROXY = os.environ.get('http_proxy', "127.0.0.1:8123")

GPGBIN = "/usr/bin/gpg2"
GPGLISTKEYS = GPGBIN + " --batch -q --with-colons --list-keys "+\
    "--keyid-format 0xlong"

GPGUPDATEKEY = GPGBIN + " --batch -q "+\
    "--keyserver-options no-honor-keyserver-url,http-proxy=%s " % (HTTP_PROXY)+\
    "--recv-keys "

def maxwait(endtime, keys):
  # how long we can sleep between each key check
  # given that this should be random we should in the long run land somewhere
  # around the half of this number, this is why it is multiplied by 1.5
  if len(keys) > 0:
    max_wait = (endtime - int(time.time()))//len(keys) * 1.5

    # make sure we have a safe minimum limit
    if max_wait < 15:
      max_wait = 15
  else:
    max_wait = 15

  return max_wait

# class for unbuffering stdout
class Unbuffered:
  def __init__(self, stream):
    self.stream = stream
  def write(self, data):
    self.stream.write(data)
    self.stream.flush()
  def __getattr__(self, attr):
    return getattr(self.stream, attr)

if __name__ == "__main__":

  sys.stdout = Unbuffered(sys.stdout)

  print("starting the refresh process")
  print("GPGUPDATEKEY: %s" % (GPGUPDATEKEY))
  print("GPGLISTKEYS: %s" % (GPGLISTKEYS))

  # building a list of the keys that we can update
  keys_to_check = list()
  for line in subprocess.check_output(shlex.split(GPGLISTKEYS)).split("\n"):
    if line.startswith("pub:-:"):
      keys_to_check.append((line.split(':')[4]))

  # we should finish in the worst case at this time
  ENDTIME=int(time.time()) + (REFRESH_LIMIT_HOURS * 3600)
  max_wait = maxwait(ENDTIME, keys_to_check)
  print("collected the keys to refresh: %s, max_wait: %s" % \
      (len(keys_to_check),max_wait))

  # random sleep at begining
  time.sleep(random.randint(1, max_wait))

  while keys_to_check:

    print("keys left to process: %s, current max_wait %s " % \
        (len(keys_to_check), max_wait))

    # pick random key to check
    keyid = random.choice(keys_to_check)

    # see if there is an update
    try:
      subprocess.check_call(shlex.split(GPGUPDATEKEY+keyid))
    except:
      # if there was a problem refreshing this key we will try
      # again on another round, not this one
      pass

    keys_to_check.remove(keyid)
    max_wait = maxwait(ENDTIME, keys_to_check)

    # random sleep between key checks
    time.sleep(random.randint(1,max_wait))
