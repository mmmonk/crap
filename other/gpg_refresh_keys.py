#!/usr/bin/env python

from __future__ import print_function

import subprocess
import shlex
import time
import random
import os

REFRESH_LIMIT_HOURS = 7*24
HTTP_PROXY = os.environ.get('http_proxy', "127.0.0.1:8123")

GPGBIN = "/usr/bin/gpg2"
GPGLISTKEYS = GPGBIN + " --batch -q --with-colons --list-keys "+\
    "--keyid-format 0xlong"

GPGUPDATEKEY = GPGBIN + " --batch -q "+\
    "--keyserver-options no-honor-keyserver-url,http-proxy=%s " % (HTTP_PROXY)+\
    "--recv-keys "

print("starting the refresh process")

# building a list of the keys that we can update
keys_to_check = list()
for line in subprocess.check_output(shlex.split(GPGLISTKEYS)).split("\n"):
  if line.startswith("pub:-:"):
    keys_to_check.append((line.split(':')[4]))

print("collected the keys to refresh: %s" % (len(keys_to_check)))

# how long we can sleep between each key check
max_wait = (REFRESH_LIMIT_HOURS*3600)//len(keys_to_check)

# make sure we have a safe minimum limit
if max_wait < 15:
  max_wait = 15

print("max_wait is : %s" % (max_wait))

# random sleep at begining
time.sleep(random.randint(10, max_wait))

while keys_to_check:
  print("keys left to process: %s" % (len(keys_to_check)))

  # pick random key to check
  keyid = random.choice(keys_to_check)

  # see if there is an update
  try:
    subprocess.check_call(shlex.split(GPGUPDATEKEY+keyid))
  except:
    # if there was a problem refreshing this key we will try
    # again on another round
    keys_to_check.remove(keyid)

  # random sleep between key checks
  time.sleep(random.randint(10,max_wait))
