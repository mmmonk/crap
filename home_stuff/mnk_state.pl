#!/usr/bin/perl

# $Id$

use strict;
use warnings;

my $batinfo="/proc/acpi/battery/BAT1/info";
my $batstat="/proc/acpi/battery/BAT1/state";
my $curtemp="/proc/acpi/thermal_zone/THRM/temperature";

my $ctemp=0;
my $max=0;
my $dmax=0;
my $cur=0;
my $rate=0;
my $bstat="";

open(B,$batinfo);
while(<B>){
  $dmax=$1 if (/design capacity:\s+(\d+)\s+mAh/);
  $max=$1 if (/last full capacity:\s+(\d+)\s+mAh/); 
}
close(B);

open(B,$batstat);
while(<B>){
  $rate=$1 if (/present rate:\s+(\d+)\s+mA/);
  $cur=$1 if (/remaining capacity:\s+(\d+)\s+mAh/);  
  $bstat=$1 if (/charging state:\s+(\S+)\n/);
}
close(B);

open(T,$curtemp);
while(<T>){
  $ctemp=$1 if (/temperature:\s+(\d+)\s+C/); 
}
close(T);

if ($bstat eq "discharging"){
  my $h=($cur/$rate);
  printf "-:%02.2f%%(%d.%02d) %dC\n",(($cur/$max)*100),int($h),(60*($h-int($h))),$ctemp;
}elsif($bstat eq "charging"){
  my $h=($max-$cur)/$rate;
  printf "+:%02.2f%%(%d.%02d) %dC\n",(($cur/$max)*100),int($h),(60*($h-int($h))),$ctemp;
}elsif($bstat eq "charged"){
  printf "=:%02.2f%% %dC\n",(($max/$dmax)*100),$ctemp;
}
