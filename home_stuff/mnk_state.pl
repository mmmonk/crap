#!/usr/bin/perl

# $Id$

use strict;
use warnings;
eval "require \"sys/syscall.ph\"";

my $syscall=1;
if ($@){
  $syscall=0;
}

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

my $line="";
if ($syscall){
  # we have syscall, this is faster
  my $fmt = "\0" x 512;
  my $dir = "/";
  my $res = syscall (&SYS_statfs, $dir, $fmt);
  # L here because we are running on 32 bits
  my ($ftype, $bsize, $blocks, $bfree, $bavail) = unpack("L5", $fmt);

  $line.="".(int((($blocks-$bavail)/$blocks)*100))."% ";
}else{
  # we don't have syscall, need to do a workaround
  open(DF,"df |");
  while(<DF>){
    next unless (/\/$/);
    $line.="".(split(" "))[4]." ";
  }
  close(DF);
}

if ($bstat eq "discharging"){
  my $h=($cur/$rate);
  $line.=sprintf "-:%02.2f%%(%d.%02d)",(($cur/$max)*100),int($h),(60*($h-int($h)));
}elsif($bstat eq "charging"){
  my $h=($max-$cur)/$rate;
  $line.=sprintf "+:%02.2f%%(%d.%02d)",(($cur/$max)*100),int($h),(60*($h-int($h)));
}elsif($bstat eq "charged"){
  $line.=sprintf "=:%02.2f%%",(($max/$dmax)*100);
}

print $line." ".$ctemp."C\n"; 
