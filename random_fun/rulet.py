#!/usr/bin/env python


def gen(x):
  # https://www.gnu.org/software/gsl/manual/html_node/Other-random-number-generators.html
  # Generator: gsl_rng_vax
  # This is the VAX generator MTH$RANDOM. Its sequence is,
  # x_{n+1} = (a x_n + c) mod m
  # with a = 69069, c = 1 and m = 2^32. The seed specifies the initial value, x_1. The period of this generator is 2^32 and it uses 1 word of storage per generator.
  return (69069*x+1)%4294967296

def loop(l,x):
  xl = 0
  for j in xrange(0,len(l)):
    xl = gen(x)
    if not xl % 36 == l[j]:
      return False
    x = xl

  for i in xrange(0,3):
    x = xl
    xl = gen(x)
    print str(xl%36)
  return True

i = 1 # 7137832
l = [27, 16, 1, 34, 31, 24, 17, 34, 35, 16, 13]

while True:

  xo = 34+36*i
  if loop(l,xo):
    break
  if xo > 4294967296: # 2^32
    print "not found"
    break
  i+=1
