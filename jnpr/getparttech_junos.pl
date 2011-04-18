#!/usr/bin/perl

# $Id$

use strict;
use warnings;
use integer;

sub usage {
  print "usage:
  $0 <options>
  
  -s <command>
    command that will be displayed

  -f <filename> 
    file to read
  ";
  exit;
};

usage if ($#ARGV<0);

my ($file, $search);

for(my $i=0;$i<$#ARGV;$i+=2) {
  if ($ARGV[$i] eq "-f" and exists($ARGV[$i+1])) { $file=$ARGV[$i+1]; next};
  if ($ARGV[$i] eq "-s" and exists($ARGV[$i+1])) { $search=$ARGV[$i+1]; next};
  usage;
}

usage if (!defined($file) or !defined($search));


open(FILE,$file) or die "$file: $!\n";
my $print=0;
while(<FILE>){
  $print=0 if /flowd|cpp0|ioc0|@.*>.*/;
  $print=1 if /$search/;
  print if $print == 1;
}
close(FILE);
