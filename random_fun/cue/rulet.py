#!/usr/bin/env python

def gen(x):
  # https://www.gnu.org/software/gsl/manual/html_node/Other-random-number-generators.html
  # Generator: gsl_rng_vax
  # This is the VAX generator MTH$RANDOM. Its sequence is,
  # x_{n+1} = (a x_n + c) mod m
  # with a = 69069, c = 1 and m = 2^32. The seed specifies the initial value, x_1. The period of this generator is 2^32 and it uses 1 word of storage per generator.
  return (69069*x+1)%4294967296

def loop(x):

  l = [27, 16, 1, 34, 31, 24, 17, 34, 35, 16, 13]

  for j in l:
    x = gen(x)
    if not x % 36 == j:
      return False

  for i in range(3):
    x = gen(x)
    print str(x%36),
  return True

i = 0 # 7137832

xo = 0
while xo < 4294967296:

  xo = 34+36*i
  if loop(xo):
    break
  i+=1
