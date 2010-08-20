#!/usr/bin/perl

# $Id$

use strict;
use warnings;

my @temp=`/usr/bin/sensors | /bin/grep Core`;

my $maxtemp=0;
foreach (@temp){
	s/^.+?(\d+)\.\d+.*/$1/;
	$maxtemp=$_ if ($_>$maxtemp);
}

open(FD,"/etc/boinc-client/global_prefs_override.xml");
my @cfg=<FD>;
close(FD);

my $cpulimit=0;

foreach (@cfg){
	if (/cpu_usage_limit/){
		chomp;	
		($cpulimit=$_)=~s/\s+<cpu_usage_limit>(\d+)\.000000<\/cpu_usage_limit>/$1/;
		if ($maxtemp<70){
			$cpulimit+=5;
			$cpulimit=100 if ($cpulimit>100);
		}else{	
			$cpulimit-=5;
			$cpulimit=10 if ($cpulimit<10);
		}
		s/<cpu_usage_limit>\d+\.000000<\/cpu_usage_limit>/<cpu_usage_limit>$cpulimit\.000000<\/cpu_usage_limit>\n/;
	}
}

open(FD,"> /etc/boinc-client/global_prefs_override.xml");
print FD @cfg;
close(FD);
exec("/usr/bin/boinc_cmd --host 127.0.0.1 --passwd \"\" --read_global_prefs_override");
