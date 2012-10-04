#!/usr/bin/env python

# $Id: 20121002$
# $Date: 2012-10-02 19:30:23$
# $Author: Marek Lukaszuk$

# based on:
# http://cpansearch.perl.org/src/KBRINT/Crypt-Juniper-0.02/lib/Crypt/Juniper.pm

import sys,re

family = ('QzF3n6/9CAtpu0O','B1IREhcSyrleKvMW8LXx','7N-dVbwsY2g4oaJZGUDj','iHkq.mPf5T')
encoding = ((1,4,32),(1,16,32),(1,8,32),(1,64),(1,32),(1,4,16,128),(1,32,64))

num_alpha = "".join(family)

a = "$9$LbHX-wg4Z"

p9 = re.search("\$9\$(.+?)",a)

out = ""
chars = p9.group(1)
prev = chars[0]
for c in chars:
  d = encoding[len(out)%len(encoding)]
  nibble = chars[0:len(d)]

