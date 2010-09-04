#!/usr/bin/perl 

# $Id$

use strict;
use warnings;
use integer;

use Expect;
use POSIX qw(:termios_h);

my $maxkids=5;

my $hostsfile=shift;
my $cmdsfile=shift;
my @cmds;

# reading commands for per host execution
open(FD,$cmdsfile) or die "$!\n";
while(<FD>){
  next if (/^\s+$/);
  chomp;
  push(@cmds,$_);  
}
close(FD);


# reading file with hosts to connect to
open(FD,$hostsfile) or die "$!\n";

$|=1;
my $kids=0; 

while (<FD>){

  $kids++;
  if (fork == 0){
    chomp;

    my $exp = Expect->new();

    foreach my $cmd (@cmds){
      print "$_ - $cmd\n";
    }

    exit;

  }else{
    if ($kids>=$maxkids){
      wait();
      $kids--;
    }
  }

}

