#!/usr/bin/perl

use strict;
use warnings;
use integer;

use POSIX qw(strftime);
use IO::Interface::Simple;
use Net::Netmask;

my $refreshtime=10;
my $font="-misc-fixed-medium-r-normal--0-0-75-75-c-0-iso8859-1";
my $sleeptime=1;

my $counttime=int($refreshtime/$sleeptime);
my $counter=$counttime;

my $txt="";

open(OSD,"| osd_cat -p bottom -A right -c green -o 20 -l 1 -d ".($sleeptime+1)." -f $font"); 
select(OSD);
$|=1;

while (){

	if ($counter==$counttime){
		my @interfaces = IO::Interface::Simple->interfaces;
		$txt="";
		foreach my $if (@interfaces){
			next if ($if=~/^lo.*/);
			next unless ($if->address);
			my $n=new Net::Netmask ($if->address,$if->netmask);	
			$txt.="$if:".$if->address."/".$n->bits()." ";
		}

		my $temp=join('',loadfile("/proc/acpi/thermal_zone/THM0/temperature"));
		chomp $temp;
		$temp=(split(" ",$temp))[1];
		$txt.="t:".$temp."C/";
		$temp=join('',loadfile("/proc/acpi/thermal_zone/THM1/temperature"));
		chomp $temp;
		$temp=(split(" ",$temp))[1];
		$txt.=$temp."C ";

		my @batt=loadfile("/proc/acpi/battery/BAT0/info");
		map{s/^.+?:\s+(\w+?|\d+?)\s+.*/$1/;chomp} @batt;
		my $fuckedup=($batt[2]*100)/$batt[1];


		my @tempa=loadfile("/proc/acpi/battery/BAT0/state");
		map{s/^.+?:\s+(\w+?|\d+?)\s+.*/$1/;chomp} @tempa;

		$txt.="b:".(($tempa[4]*100)/$batt[2])."%";
		
		unless ($tempa[2]=~/discharging/){
			$txt.="=";
		}

		$txt.=" (".$fuckedup."%)";
	}

#	my $time = strftime "%Y%m%d %H%M%S",localtime(time());

	$counter--;
	$counter=$counttime if ($counter==0);
	print OSD $txt." ",time,"\n"; 
	
	sleep $sleeptime;
}
close(OSD);


sub loadfile{
	my $file=shift;
	
	open(FD,$file);
	my @loaded_data=<FD>;
	close(FD);

	return @loaded_data;
}
