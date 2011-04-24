#!/usr/bin/perl

# $Id$

use strict;
use warnings;
use integer;

my $file="/proc/net/xt_recent/ssh_allow";

my %ip;
open(LAST,"/usr/bin/last -i | ") or die "can't run a command";
while(<LAST>){
  next unless (/pts/);
  $_=(split(" ",$_))[2];
  $ip{$_}=1;
}
close(LAST);

foreach my $h (keys %ip){
  open(my $fh,">",$file);
  print $fh "+$h\n";
  close($fh);
}

#print time,"\n";
#open(SA,$file);
#while(<SA>){
#  s/src=(.+?) .* last_seen: (\d+) .*/$1 $2/;
#  print;
#}
#close(SA);
