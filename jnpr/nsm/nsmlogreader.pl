#!/usr/bin/perl

# $Id$

use strict;
use warnings;
use integer;

my $c=0;
my $ts="";
my @data;

my ($date,$time,$d,$m,$Y);

while(<>){
  if (/^(\d{4}\/\d{2}\/\d{2}-\d{2}:\d{2}:\d{2}\.\d{3}) /){
    $ts=$1;
    $c=0;
    push(@data,"$ts 000 $_");
    next;
  }
  
  if (/^\[(\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}:\d{2}\.\d{3})\] /){
    ($date,$time)=split(" ",$1);
    ($m,$d,$Y)=split('/',$date);
    $ts="$Y/$m/$d-$time";
    $c=0;
    push(@data,"$ts 000 $_");
    next;
  }
  
  next if ($ts eq "");

  $c++;
  if ($c<10) {
    push(@data,"$ts 00$c $_");
    next;
  }
  if ($c<100) {
    push(@data,"$ts 0$c $_");
    next;
  }

  push(@data,"$ts $c $_");
}

foreach (sort @data){
  print;
}
