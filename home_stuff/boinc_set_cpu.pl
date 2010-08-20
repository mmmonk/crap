#!/usr/bin/perl

# $Id$

use strict;
use warnings;

my $cpulimit=shift;

die ":P" unless ($cpulimit);

die ":P" if ($cpulimit>100 or $cpulimit<0); 

open(FD,"/etc/boinc-client/global_prefs_override.xml");
my @cfg=<FD>;
close(FD);

foreach (@cfg){
	s/<cpu_usage_limit>\d+\.000000<\/cpu_usage_limit>/<cpu_usage_limit>$cpulimit\.000000<\/cpu_usage_limit>/ if (/cpu_usage_limit/);
}

open(FD,"> /etc/boinc-client/global_prefs_override.xml");
print FD @cfg;
close(FD);
exec("/usr/bin/boinc_cmd --host 127.0.0.1 --passwd \"\" --read_global_prefs_override");
