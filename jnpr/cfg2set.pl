#!/usr/bin/perl

use strict;
use integer;
use warnings;

my @n;
while(<>){
  chomp;
  s/(\r|\n)//g;
  s/^\s*//;
  if (/\{\s*$/){
    s/^(.+?)\s+\{/$1/;
    push(@n,$1);
  }elsif (/^\s*\}\s*$/) {
    pop(@n);
  }else{
    if (length(@n) > 0){ 
      print "set ";  
    }
    foreach my $a (@n){
      print $a." ";
    }
    print $_."\n";
  }
}
