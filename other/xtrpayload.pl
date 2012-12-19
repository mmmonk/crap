#!/usr/bin/perl

# $Id: 20121219$
# $Date: 2012-12-19 13:18:09$
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
It uses tcpdump and ngrep.\n";
}

my %pairs=();

# finding unique communication streams
my $cmd = "tcpdump -nr $file \"$bpf\"";
open(CMD,"$cmd |");
while(<CMD>){
  chomp;
  # extracting unique src dst pairs, should work for tcp and udp
  s/^\S+? \S+? (\S+?)\.(\d+) > (\S+?)\.(\d+): .*/$1 $2 $3 $4/;
  $pairs{$_}=1;
}
close(CMD);

# extracting each stream
foreach my $pair (keys %pairs){
  my @a=split(" ",$pair);
  if ($a[0] and $a[1] and $a[2] and $a[3]) {
    print "[+] extracting payload from stream src=$a[0]:$a[1] dst=$a[2]:$a[3]\n";

    $cmd = "ngrep -qxI $file \"\" src host $a[0] and src port $a[1] and dst host $a[2] and dst port $a[3]";
    open(CMD,"$cmd | ");
    open(OUT,"> out_$ts\_$a[0]\_$a[1]\_$a[2]\_$a[3].bin");
    while(<CMD>){
      next unless (/^\ \ \S\S\ \S\S/);
      # extracting only the hex values
      s/^\ \ (.+?)\ {4}(.+?)\ {3}.*/$1 $2/;
      # converting the hex output to real characters
      print OUT map(chr(hex($_)),split(" "));
    }
    close(CMD);
    close(OUT);
  }
}
