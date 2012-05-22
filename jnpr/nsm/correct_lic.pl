#!/usr/bin/perl

# $Id$

use strict;
use warnings;
use integer;

my $file=shift;
open(FD,$file) or die "can't open file: $!\n";

my $devname=shift;

my %vsyses;

my $maxvlan=0;
my $indev=0;
my $indevobj=0;
my $invsys=0;
my $inlic=0;

while (<FD>){
  $indevobj=1 if (/^deviceobj/);
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
      }
      $inlic=0 if (/^\s+:.+?\s*\(\s*$/ and $inlic==1);
      $inlic=1 if (/^\s+:licensekey\s*\(\s*$/);
      if ($inlic==1){
        if (/^\s+:max_vlan_num\s*\((\d+)\)\s*$/){
          $maxvlan=$1;
        }
      }
    }
    $indevobj=0 if (/^END/);
  }
}

sysseek(FD,0,0);

$indev=0;
$indevobj=0;
$inlic=0;
my $inmem=0;
my %members;

while (<FD>){
  $indevobj=0 if (/^END/);
  $indevobj=1 if (/^deviceobj/);
  if ($indevobj==1){
    $indev=0 if (/^\)/);
    if (/^\s+:\d+\s+\((.+?)\s*$/i){
      $indev=1 if (exists($vsyses{$1}));
    }
    if ($indev==1){
      $inmem=0 if (/^\s+\)\s*$/);
      $inmem=1 if (/^\s+:members \(/);
      if ($inmem==1){
        if (/^\s+: \(\"\&(.+?)\"\)/){
          push @{ $members{$1} }, "1";
        }
      }
    }
  }
}

sysseek(FD,0,0);

$indev=0;
$indevobj=0;
$inlic=0;

while (<FD>){
  $indevobj=0 if (/^END/);
  $indevobj=1 if (/^deviceobj/);
  if ($indevobj==1){
    $indev=0 if (/^\)/);
    if (/^\s+:(\d+)\s+\((.+?)\s*$/i){
      my $dev=$1;
      foreach my $mem (keys %members){
        $mem=~s/.*?\.(\d+)$/$1/;
        $indev=$dev if ($mem eq $dev);
      }
      $indev=1 if (exists($vsyses{$2}));
    }
    if ($indev > 0){
      if (/^\s+:clusterowner \(\"\&(\d+)\./){
        if (exists($members{"$1.deviceobj.$indev"})){
          $indev=1;
        }
      }
      if ($indev==1){  
        $inlic=0 if (/^\s+:.+?\s*\(\s*$/ and $inlic==1);
        $inlic=1 if (/^\s+:licensekey\s*\(\s*$/);
        if ($inlic==1){
          s/^(\s+:max_vlan_num\s*\()\d+(\)\s*)$/$1$maxvlan$2/;
        }
      }
    }
  }
  print;
}


close(FD)

