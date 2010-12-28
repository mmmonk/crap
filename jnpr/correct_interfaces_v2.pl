#!/usr/bin/perl

use strict;
use warnings;
use integer;


my $file=shift;
my $devname=shift;

die "usage: $0 input_file name_of_the_cluster_with_vsys\n" unless ($devname);

open(FD,$file) or die "can't open file: $!\n";

my %vsyses;

my $maxvlan=0;
my $indev=0;
my $indevobj=0;
my $invsys=0;
my $inlic=0;

my $devoffset=0;

my $spaces=" ";

while (<FD>){
  print if ($indevobj==0); 
  if (/^deviceobj/){
    $indevobj=1;
    $devoffset=tell(FD);
    $devoffset=($devoffset<=50) ? 0 : $devoffset-50;
  }  
  if ($indevobj==1){
    $indev=0 if (/^\)/);
    $indev=1 if (/^\s+:\d+\s+\($devname\s*$/i);
    if ($indev==1){
      $invsys=0 if (/^\s+:.+?\s*\(\s*$/ and $invsys==1);
      $invsys=1 if (/^\s+:vsys \(/);
      if ($invsys==1){
        if (/^\s+:\d+\s+\((.+?)\s+/){
          push @{ $vsyses{$1} }, "1";
        }
        if (/^\s+:vsys-device \(\"\&(.+?)\"\)\s*$/){
          push @{ $vsyses{$1} }, "1";
        }
      }
    }
    if (/^END/){
      $indevobj=0;
      last;
    }

  }
}

seek(FD,$devoffset,0);

$indev=0;
$indevobj=0;
$inlic=0;
my $vsysoffset=0;
my $inmem=0;

while (<FD>){
  if (/^END/){
    $indevobj=0;
    last;
  }
  $indevobj=1 if (/^deviceobj/);
  if ($indevobj==1){
    $indev=0 if (/^\)/);
    if (/^\s+:\d+\s+\((.+?)\s*$/i){
      $indev=1 if (exists($vsyses{$1}));
    }else{
      $vsysoffset=tell(FD);
    }
    if ($indev==1){
      $inmem=0 if (/^\s+\)\s*$/);
      $inmem=1 if (/^\s+:members \(/);
      if ($inmem==1){
        if (/^\s+: \(\"\&(.+?)\"\)/){
          push @{ $vsyses{$1} }, "1";
        }
      }
    }else{
      if (/^\s+:vsysname \((.+?)\)\s*$/){
        $indev=1 if (exists($vsyses{$1}));
        seek(FD,$vsysoffset,0); 
      }
    }
  }
}

seek(FD,$devoffset,0);

$indev=0;
$indevobj=0;
$inlic=0;
my $print=0;
$vsysoffset=0;
$spaces=" ";

while (<FD>){
  $indevobj=0 if (/^END/);
  if (/^deviceobj/){
    $indevobj=1;
    $print=1;
    next;
  }
  if ($indevobj==1){
    $indev=0 if (/^\)/);
    if (/^\s+:clusterowner \(\"\&(.+?)\"\)/){
      $indev=1 if (exists($vsyses{"$1"}));
    }
    if ($indev==1){  
      next if (/^\s+:.*?\(\"ethernet4\/1\.124\"\)\s*$/);
      if (/^$spaces\)\s*$/ and $inlic==1){
        $inlic=0;
        $spaces=" ";
        next;
      }
      if (/^(\s+):.*?\(\"ethernet4\/1\.124\"\s*$/){
        $inlic=1;
        $spaces=$1;
      }
      if ($inlic==1){
        next;
      }
    }else{
      if (/^\s+:vsysname \((.+?)\)\s*$/){
        $indev=1 if (exists($vsyses{$1}));
      }
    }
  }
  print if ($print==1);
}

close(FD)

