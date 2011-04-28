#!/usr/bin/perl

# $Id$

use strict;
use warnings;

require "sys/syscall.ph";

my $fmt = "\0" x 512;
my $dir = "/";
my $res = syscall (&SYS_statfs, $dir, $fmt);
# Q below because we are running on 64 bit - man statfs
my ($ftype, $bsize, $blocks, $bfree, $bavail) = unpack("Q5", $fmt);

my $file="/var/local/datausage.dat";

if ( -f $file){
  open(FD,$file);
  my $line=<FD>;
  close(FD);
  my @stat=split(" ",$line); 
  print "".(int((($blocks-$bavail)/$blocks)*100))."% ".(int(($stat[3]/1024)*100)/100)."/".(int(($stat[2]/1024)*100)/100)."\n";
}
