#!/usr/bin/perl

use strict;
use warnings;
use integer;

my $file = shift;

unless ($file) {
  print "usage: $0 <xdif_file>

  This utility converts xdif file to init file format
  Please use it on xdif files that have single container inside (ie. rb_firewall)\n";
  exit 1;
}

open(FD,$file) or die "$!";
while(<FD>){
  if (/^\)/){
    print "#####TUPLE_DATA_END#####\n";
    next;
  }
  if (/^\((.{8})(.{4})(.{4})\s*/){
    print "#####TUPLE_DATA_BEGIN#####\n";
    print hex($1),"\n",hex($3),"\n";
    next;
  }
  next if (/^\S+/);
  s/^\t//;
  s/^:\d+\s+//;
  print;
}
close(FD);
