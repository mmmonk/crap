#!/usr/bin/perl

# $Id$

use strict;
use warnings;

my $datafile="/var/local/datausage.dat";

my $limit=500; # in gigabytes

my @ts=localtime(time);

$ts[4]++;
$ts[4]="0".$ts[4] if ($ts[4]<10);
$ts[3]="0".$ts[3] if ($ts[3]<10);

my $cts=($ts[5]+1900).$ts[4].$ts[3];
my $cmts=($ts[5]+1900).$ts[4];

my $curdata=0;

open(FD,"ifconfig eth0 |") or die "$!\n";
while(<FD>){
  $curdata=int($1/1048576)+int($2/1048576) if (/RX bytes:(\d+) .+ TX bytes:(\d+) .*/);
}
close(FD);

my $lts=0;
my $lbw=$curdata;
my $lbm=0;
my $lbd=0;

if (open(BW,$datafile)){
  ($lts,$lbw,$lbm,$lbd)=split(" ",<BW>);
  my $mtime=time()-(stat(BW))[9];
  close(BW);
  open(UT,"/proc/uptime") or die "$!\n";
  my $uptime=int((split(" ",<UT>))[0]);
  close(UT);
  if ($mtime>$uptime){
    $lbw=0;
  }
}
if ($lts==$cts){
  $lbm+=$curdata-$lbw;
  $lbd+=$curdata-$lbw;
}else{
  $lbd=$curdata-$lbw;
  $lts=~s/\d\d$//;
  if ($lts==$cmts){
    $lbm+=$curdata-$lbw;
  }else{
    $lbm=$curdata-$lbw;
  }
}
open(BW,"> $datafile") or die "$!\n";
print BW "$cts $curdata $lbm $lbd";
close(BW);

my $print=0;
open(MOTD,"/etc/motd") or die "$!\n";
open(NMOTD,"> /etc/motd_new") or die "$!\n";
while(<MOTD>){
  if (/^Data usage/){
    printf NMOTD "Data usage this month %.2f G (limit %d G), today %d M.\n", (($lbm/1024),$limit,$lbd);
    $print=1;
  }else{ 
    print NMOTD;
  }
}
if ($print==0){
  printf NMOTD "Data usage this month %.2f G (limit %d G), today %d M.\n", (($lbm/1024),$limit,$lbd);
}
close(NMOTD);
close(MOTD);
rename("/etc/motd_new","/etc/motd");
