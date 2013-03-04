#!/usr/bin/env python

# $Id: 20130304$
# $Date: 2013-03-04 17:23:08$
# $Author: Marek Lukaszuk$

# docs:
# https://tools.ietf.org/html/rfc5798
# https://tools.ietf.org/html/rfc3768
# https://tools.ietf.org/html/rfc2338

from scapy.all import *

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('-s','--source',help='source IP address, either IPv4 or IPv6, if not set uses the corresponding interface address')

(arg,rest_argv) = parser.parse_known_args(sys.argv)

