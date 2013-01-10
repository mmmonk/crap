#!/usr/bin/perl

# $Id: 20121121$
# $Date: 2012-11-21 11:15:07$
# $Author: Marek Lukaszuk$

use strict;
use warnings;

require "sys/syscall.ph";

my $datafile = "/var/local/datausage.dat";

my $limit = 500; # in gigabytes

my @ts = localtime(time);

$ts[4] ++;
$ts[4] = "0".$ts[4] if ($ts[4]<10);
$ts[3] = "0".$ts[3] if ($ts[3]<10);

my $cts = ($ts[5] + 1900).$ts[4].$ts[3]; # current day
my $cmts = ($ts[5] + 1900).$ts[4];       # current month

my $ctx = 0; # TX counter
my $crx = 0; # RX counter

open(FD,"ifconfig eth0 |") or die "$!\n";
while(<FD>){
  if (/RX bytes:(\d+) .+ TX bytes:(\d+) .*/){
    $crx = int($1/1048576);
    $ctx = int($2/1048576);
  }
}
close(FD);

my $curdata = $crx + $ctx;
my $lts = 0;
my $lbw = $curdata;
my $lbm = 0;
my $lbd = 0;
my $rx = 0;
my $tx = 0;
my $mrx = $crx;
my $mtx = $ctx;

if (open(BW,$datafile)){
  ($lts,$lbw,$lbm,$lbd,$rx,$tx,$mrx,$mtx)=split(" ",<BW>);
  my $mtime = time() - (stat(BW))[9];
  close(BW);
  open(UT,"/proc/uptime") or die "$!\n";
  my $uptime = int((split(" ",<UT>))[0]);
  close(UT);
  if ($mtime>$uptime){
    $lbw = 0;
    $rx = 0;
    $tx = 0;
  }
}

$lbm += $curdata - $lbw;
$lbd += $curdata - $lbw;
$mrx += $crx - $rx;
$mtx += $ctx - $tx;

unless ($lts == $cts){ # reseting daily limit
  $lbd = $curdata - $lbw;
  $lts =~ s/\d\d$//;
  unless ($lts == $cmts){ # reseting monthly limit
    $lbm = $curdata - $lbw;
    $mrx = $crx - $rx;
    $mtx = $ctx - $tx;
  }
}
open(BW,"> $datafile") or die "$!\n";
print BW "$cts $curdata $lbm $lbd $crx $ctx $mrx $mtx";
close(BW);

my $fmt = "\0" x 512;
my $dir = "/";
my $res = syscall (&SYS_statfs, $dir, $fmt);
# Q below because we are running on 64 bit - man statfs
my ($ftype, $bsize, $blocks, $bfree, $bavail) = unpack("Q5", $fmt);


my $print=0;
open(MOTD,"/etc/motd.tail") or die "$!\n";
open(NMOTD,"> /etc/motd_new") or die "$!\n";
while(<MOTD>){
  next if (/^Current disk usage /);
  if (/^Data usage/){
    printf NMOTD "Data usage this month %.2f G (limit %d G).\nCurrent disk usage %d%%.\n", (($lbm/1024),$limit),(int((($blocks-$bavail)/$blocks)*100));
    $print=1;
  }else{ 
    print NMOTD;
  }
}
if ($print==0){
  printf NMOTD "Data usage this month %.2f G (limit %d G).\nCurrent disk usage %d%%.\n", (($lbm/1024),$limit),(int((($blocks-$bavail)/$blocks)*100));
}
close(NMOTD);
close(MOTD);
rename("/etc/motd_new","/etc/motd.tail");
system("/bin/cp /etc/motd.tail /etc/motd");

