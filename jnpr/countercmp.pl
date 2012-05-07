#!/usr/bin/perl

use strict;
use warnings;
use integer;

my $file1 = shift;
my $file2 = shift;

my $tdiff = shift || 0;

unless ($file2) {
  print "Usage: $0 file1 file2 [time_in_seconds]
  
  This will try to compare counters between file1 and file2.
  It will also calculate delta between those counters.
  If the time_in_seconds is specified it will divde delta 
  by this value.\n";
  exit(1);
}

open(F1,$file1) or die "$!";
open(F2,$file2) or die "$!";

my $l1; my $l2;

while($l1=<F1>){
  $l2 = <F2>;
  
  $l1=~s/(\t|\n|\r)/ /g;
  $l1=~s/^\s+//;
  $l2=~s/(\t|\n|\r)/ /g;
  $l2=~s/^\s+//;

  my $haveit=0;
  my $nl1=" "; my $cl1=0;
  my $nl2=" "; my $cl2=0;
  
  if ($l1=~/^(.+) (\d+)\s*$/){
    $nl1=$1;
    $cl1=$2;
    $haveit=1;
  } else {
    $l1=~/^\s*(\d+) (.*)$/;
    $cl1=$1;
    $nl1=$2;
    $haveit=1;
  }
  if ($l2=~/^(.+) (\d+)\s*$/){;
    $nl2=$1;
    $cl2=$2;
  } else {
    $l2=~/^\s*(\d+) (.*)$/;
    $cl2=$1;
    $nl2=$2;
  }

  if ($haveit==1) {
    if (defined($nl1) and defined($nl2) and $nl1 eq $nl2 and $cl1 ne $cl2){
      my $diff=0;
      if ($cl1 > $cl2){
        $diff=$cl1-$cl2;
      }else{
        $diff=$cl2-$cl1;
      }
      if ($tdiff == 0) {
        print "$nl1 1: $cl1  2: $cl2  d: $diff\n";
      } else {
        print "$nl1 1: $cl1  2: $cl2  d: $diff  d/s: ".($diff/$tdiff)."\n";
      }
    }
  }
}
close(F1);
close(F2);
