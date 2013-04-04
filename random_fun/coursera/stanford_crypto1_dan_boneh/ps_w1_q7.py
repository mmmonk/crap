#!/usr/bin/env python

m = "attack at dawn"
c = "6c73d5240a948c86981bc294814d".decode('hex')
m2 = "attack at dusk"

key = "".join([ chr(ord(m[i])^ord(c[i])) for i in range(len(m))])
print "".join([ chr(ord(key[i])^ord(m2[i])) for i in range(len(m2))]).encode('hex')

