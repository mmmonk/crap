#!/usr/bin/env python

# generate passwords based on the URI+somerandom stuff

# TODO:
# - add a choice of possible strings characters, although if the site doesn't
#   allow special characteres they have some other issues,
# - maybe add a limit on the lenght of the password,
# - maybe SHA256 is good enough, and there is no need for SHA512?

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

  p = argparse.ArgumentParser(description='Simple recoverable passwords '+\
      'generator - based on URI and a secret')
  p.add_argument('-uri', '-u', required=True, help="URI, proto://user@fqdn")
  p.add_argument('-secret', '-s', required=True, help="secret")
  args = p.parse_args()

  PASSCHARS = string.letters+string.digits+string.punctuation

  print passgen(args.uri, args.secret, PASSCHARS)
