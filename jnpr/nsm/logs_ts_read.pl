#!/usr/bin/perl

use strict;
use warnings;
use integer;

use POSIX;

my $mpath = "/var/netscreen/DevSvr/logs/";
my $ff = chr(255);

opendir(DIR,$mpath) or die "$!\n";
while(my $sdir = readdir(DIR)){
  next unless ($sdir =~ /^20\d{6}$/);
  
  my $file = $mpath."/".$sdir."/"."logs.0";
  
  if ( -f $file ) { 
    open(FD,$file) or die "$!\n";
    my $dat = join("",<FD>);
    close(FD);

    while($dat=~/(....).{52}$ff{12}/gs){
      print POSIX::asctime(gmtime(unpack("L",$1)));
    }
  }
}

