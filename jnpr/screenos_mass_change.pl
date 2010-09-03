#!/usr/bin/perl 

# $Id$

use strict;
use warnings;
#use integer;
use POSIX ":sys_wait_h";

srand(time());
#use Expect;


my $maxkids=5;

my $pids=0; 
my $i=0;

while ($i<1000){

  $pids++;
  $i++;
  if (fork == 0){
    my $sleeptime = int(rand($i%10))+1;  
    sleep $sleeptime; 
    print "[k] $i ($pids) - slept for $sleeptime \n";
    exit;

  }else{
    if ($pids>=$maxkids){
      wait();
      $pids--;
    }
    print "[p] $i - $pids\n";
  }

}

