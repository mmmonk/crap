#!/usr/bin/env python

# http://www.pythonchallenge.com/pc/def/map.html

import string

t = "g fmnc wms bgblr rpylqjyrc gr zw fylb. rfyrq ufyr amknsrcpq ypc dmp. bmgle gr gl zw fylb gq glcddgagclr ylb rfyr'q ufw rfgq rcvr gq qm jmle. sqgle qrpgle.kyicrpylq() gq pcamkkclbcb. lmu ynnjw ml rfc spj."

print string.translate(t,string.maketrans("abcdefghijklmnopqrstuvwxyz","cdefghijklmnopqrstuvwxyzab"))

print string.translate("map",string.maketrans("abcdefghijklmnopqrstuvwxyz","cdefghijklmnopqrstuvwxyzab"))
