#!/usr/bin/perl

# $Id: 20120903$
# $Date: 2012-09-03 09:39:55$
# $Author: Marek Lukaszuk$

# this script converts this to something that wireshark can open
# 8550430.0: tunnel.310(it) vpn=VPN1 type=ipsec proto=0x0800
#              10.220.61.5 -> 224.0.0.5/89
#              vhl=45, tos=c0, id=60251, frag=0000, ttl=1 tlen=68
#              ospf:ver=2, type=1, len=48
#              45 c0 00 44 eb 5b 00 00 01 59 a5 5f 0a dc 3d 05     E..D.[...Y._..=.
#              e0 00 00 05 02 01 00 30 0a dc 00 fe 00 00 00 00     .......0........
#              a8 e5 00 00 00 00 00 00 00 00 00 00 ff ff ff fc     ................
#              00 0a 02 01 00 00 00 28 00 00 00 00 00 00 00 00     .......(........
#              0a dc 3c 03                                         ..<.

use strict;
use warnings;

my $seen = 0;
my $inside = 0;

while(<>){

  $inside = 1 if (/vpn=/);

  if ($inside == 1) {
    s/\((o|i)t\)/($1)/;
    s/vpn=.*$/len=1500:def012345678->123456789abc\/0800/;
    if ($seen == 0 and /^(\s+)..\ ..\ ..\ ..\ ..\ /) {
      print $1."12 34 56 78 9a bc de f0 12 34 56 78 08 00\n";
      $seen = 1;
    }
  }

  if ($inside == 1 and /^\s*$/){
    $seen = 0;
    $inside = 0;
  }

  print;
}
