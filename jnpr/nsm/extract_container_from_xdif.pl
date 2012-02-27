#!/usr/bin/perl
#

use strict;
use warnings;
use integer;


my $container=$1;

unless ($container){
  print "usage: cat xdif_file | $0 container_name\n";
  exit 1;
}

my $p = 0;
while(<>){
  
}
