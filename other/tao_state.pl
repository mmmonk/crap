#!/usr/bin/perl

# $Id$

use strict;
use warnings;

require "sys/syscall.ph";

my $line="";
for (("/","/home")){
  my $fmt = "\0"x512;
  my $dir = $_; 
  my $res = syscall (&SYS_statfs, $dir, $fmt);
  # Q below because we are running on 64 bit - man statfs
  my ($ftype, $bsize, $blocks, $bfree, $bavail) = unpack("Q5", $fmt);

  $line.="$dir ".(int((($blocks-$bavail)/$blocks)*100))."% ";
}

print $line."\n";
