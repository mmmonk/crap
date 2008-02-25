#!/usr/bin/perl -W

# Author: Marek Lukaszuk <m.lukaszuk<at>gmail.com>
# Copyright (c) 2005, Marek £ukaszuk 
# BSD License at http://monkey.geeks.pl/bsd/

use LWP::UserAgent;
$ua = LWP::UserAgent->new;
$ua->agent("Mozilla - v9.5");

# Create a request
my $req = HTTP::Request->new(GET => 'http://nntime.com/proxy/');
my $res = $ua->request($req);
# Check the outcome of the response
exit unless ($res->is_success);
my $out=join(" ",$res->content);
$out=~s/\n/ /g;

my @proxylist=$out=~/(\d+\.\d+\.\d+\.\d+:\d+)/g;
my @linklist=$out=~/(\/proxy\/proxy-list-\d+\.htm)/g;

foreach my $link (@linklist){
	$req = HTTP::Request->new(GET => "http://nntime.com$link");
	$res = $ua->request($req);
	next unless ($res->is_success);
	$out=join(" ",$res->content);
	$out=~s/\n/ /g;
	my @temp=$out=~/(\d+\.\d+\.\d+\.\d+:\d+)/g;
	push(@proxylist,@temp);
}

open(PROXY,"> proxylist.txt");
print PROXY (join("\n",@proxylist));
close(PROXY);
