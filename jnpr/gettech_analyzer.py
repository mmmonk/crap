#!/usr/bin/env python

import sys

GetCommands = [
	'get admin auth',
	'get arp',
	'get asp',
	'get auth',
	'get av',
	'get cav',
	'get chassis',
	'get config',
	'get counter',
	'get dns',
	'get envar',
	'get file',
	'get fresno',
	'get gbic',
	'get ha',
	'get imp',
	'get iocard',
	'get jupiter',
	'get license-key',
	'get mac-learn',
	'get memory',
	'get net-pak',
	'get nvram',
	'get os',
	'get performance',
	'get pim',
	'get pki ldap-run',
	'get route',
	'get sat',
	'get session',
	'get system',
	'get tcp',
	'get vpnmonitor',
	'get vrouter protocol bgp',
	'get vrouter protocol nhrp',
	'get vrouter protocol ospf',
	'get vrouter protocol pim',
	'get vrouter protocol rip'
]


try:
	fs = open(sys.argv[1],'r')
except:
	print "usage: "+sys.argv[0]+" get_tech_file"
	sys.exit(2)


for line in fs.readlines():
	if 'get ' in line:
		FuncCount = 0
		for getline in GetCommands:
			if getline in line:
				break
			FuncCount=FuncCount+1
		print FuncCount
