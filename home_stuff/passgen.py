#!/usr/bin/env python

# generate passwords based on the URI+somerandom stuff

import hashlib
import string
import argparse

def passgen(uri, secret, passchars, halgo="sha512", iterations=10000):
  """
  a very simple "random" password generator for a given website url
  without needing to record it
  """
  hmac = hashlib.pbkdf2_hmac(halgo, uri, secret, iterations)
  return "".join([passchars[ord(a)%len(passchars)] for a in hmac])

if __name__ == "__main__":

  p = argparse.ArgumentParser(description='Simple password generator')
  p.add_argument('-uri', '-u', required=True, help="URI")
  p.add_argument('-secret', '-s', required=True, help="secret")
  args = p.parse_args()

  PASSCHARS = string.letters+string.digits+string.punctuation

  print passgen(args.uri, args.secret, PASSCHARS)
