#!/usr/bin/perl

use strict;
use warnings;
use integer;

my $mpath = "/var/netscreen/DevSvr/logs/";

my $limit = 10;
my @top;
my @counts;

my $current = 0; 
my $last = 0;
my $count = 1;

for(my $i=0;$i<$limit-1;$i++){
  $counts[$i] = 0;
  $top[$i] = 0;
}

opendir(DIR,$mpath) or die "$!\n";
while(my $sdir = readdir(DIR)){
  next unless ($sdir =~ /^20\d{6}$/);
  
  my $file = $mpath."/".$sdir."/"."logs.0";
  
  if ( -f $file ) { 
    open(FD,$file) or die "$!\n";
    binmode(FD);
    my $null; my $ts;
    read(FD,$null,12);
    while(read(FD,$ts,4)) {
      $current = unpack("L",$ts);
      if ( $last == $current ){
        $count++;
      } else {
        if ($counts[0] <= $count) {
          for (my $i=$limit-2;$i>=0;$i--){
            $top[$i+1] = $top[$i];
            $counts[$i+1] = $counts[$i];
          }
          $top[0] = $last;
          $counts[0] = $count;
        }
        $last = $current;
        $count = 1;
      }
      last unless (read(FD,$null,96));
    }
    close(FD);
  }
}

for(my $i=0;$i<$limit-1;$i++){
  print $counts[$i]." - ".gmtime($top[$i])."\n";
}
