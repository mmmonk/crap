#!/usr/bin/env python

fs = open('get-tech-support-10102008.txt','r')

for line in fs.readlines():
	if 'get ' in line:
		print line
