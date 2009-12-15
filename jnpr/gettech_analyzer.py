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


FuncCommands = [
	'get_admin_auth',
	'get_arp',
	'get_asp',
	'get_auth',
	'get_av',
	'get_cav',
	'get_chassis',
	'get_config',
	'get_counter',
	'get_dns',
	'get_envar',
	'get_file',
	'get_fresno',
	'get_gbic',
	'get_ha',
	'get_imp',
	'get_iocard',
	'get_jupiter',
	'get_license-key',
	'get_mac-learn',
	'get_memory',
	'get_net-pak',
	'get_nvram',
	'get_os',
	'get_performance',
	'get_pim',
	'get_pki_ldap-run',
	'get_route',
	'get_sat',
	'get_session',
	'get_system',
	'get_tcp',
	'get_vpnmonitor',
	'get_vrouter_protocol_bgp',
	'get_vrouter_protocol_nhrp',
	'get_vrouter_protocol_ospf',
	'get_vrouter_protocol_pim',
	'get_vrouter_protocol_rip'
]

def get_envar(input):
    print input
    

try:
	fs = open(sys.argv[1],'r')
except:
	print "usage: "+sys.argv[0]+" get_tech_file"
	sys.exit(2)

FuncCount = 0
for line in fs.readlines():
    if FuncCount > 0:
        fname = FuncCommands[FuncCount]
        print fname
        f = locals()[fname]
        f() 

	if 'get ' in line:
		FuncCount = 0
		for getline in GetCommands:
			if getline in line:
				break
			FuncCount=FuncCount+1
        print str(FuncCount)+" "+line
