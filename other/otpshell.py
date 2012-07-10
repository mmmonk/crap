#!/usr/bin/python 

# idea from http://pastebin.com/dSJbGSBD

shell = "/usr/bin/tcsh"

from time import time,sleep
from struct import pack,unpack
from hmac import HMAC
from hashlib import sha1
from base64 import b32decode
import os
import sys


os.execv(shell,sys.argv)
