#!/usr/bin/perl

use strict;
use integer;
use warnings;
use POSIX;

my $bigday=1196434800;
my $sec = time;
my $ltime=asctime(localtime($sec));


my $txtb;my $diff;

if ($sec < $bigday){
        $txtb="TTL ";
        $diff=$bigday-$sec;
}else{
        $txtb="";
        $diff=$sec-$bigday;
}

my ($min,$hour,$day,$week); 

$min=0;$hour=0;$day=0;$week=0;

$sec=$diff;
if ($diff > 59){
        $sec=$diff%60;
        $diff=$diff/60;
        $min=$diff;
        if ($diff > 59){
                $min=$diff%60;
                $diff=$diff/60;
                $hour=$diff;
                if ($diff > 23){
                        $hour=$diff%24;
                        $diff=$diff/24;
                        $day=$diff;
                        if ($diff > 6){
                                $day=$diff%7;
                                $diff=$diff/7;
                                $week=$diff;
                        }
                }
        }
}
my $text=$txtb.$week."w ".$day."d ".$hour."h ".$min."m"; 

print "Marek £ukaszuk\n---=== $text ===---\n";

