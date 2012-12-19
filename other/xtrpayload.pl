#!/usr/bin/perl

# $Id: 20121219$
# $Date: 2012-12-19 20:59:19$
# $Author: Marek Lukaszuk$

use strict;
use warnings;
use integer;

my $file=shift;
my $bpf=shift;
my $ts=time();

unless ($bpf){
  die "Usage: $0 filename.pcap bpf_filter

This script will extract payload from the streams it finds in the
filename.pcap using the provided bpf filter.
It uses ngrep.\n";
}

my $conv = "";
my $buff = "";

# finding unique communication streams
open(CMD,"ngrep -qxlI $file \"$bpf\" |");
while(<CMD>){
  chomp;
  if (/^\S+ (\S+?):(\d+) -> (\S+?):(\d+) /){
    if ($conv ne "" and $buff ne ""){
      open(OUT,">> $conv");
      print OUT map(chr(hex($_)),split(" ",$buff));
      close(OUT);
    }
    $buff = "";
    $conv = "out_$1_$2_$3_$4_$ts.bin";
    print "$conv ==\n";
  }
  if (/^\s+(.+?)\ {4}(.+?)\ {3}.*/) {
    $buff .= "$1 $2 ";
  }
}
close(CMD);
