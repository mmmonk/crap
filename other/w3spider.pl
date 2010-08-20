#!/usr/bin/perl

# $Id$

#

#

use strict;
use warnings;
use integer;

use LWP::UserAgent;
use threads('stack_size' => 16384,'exit' => 'threads_only');

sub recursGet;

my %visited;

my $url = shift;
$url=~s/\/\s*$//;

$url=~/http:\/\/(.+?)($|\/|\s)/;
my $host=$1;

my $agent="Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; .NET CLR 1.1.4322";

my $ua = LWP::UserAgent->new;
$ua->agent($agent);

recursGet($ua,$url);

sub recursGet{
	my $ua=shift;
	my $url=shift;

	print "=> $url\n";
	$visited{$url}=1;
	my $req = HTTP::Request->new( GET => "$url");
	my $res = $ua->request($req);
	if ( $res->is_success ) {
		my $webtext = join(" ", $res->content );
		$webtext=~s/\s+/ /g;
		while ($webtext=~/href ?= ?"?(.+?)("| )/gi){
			my $link=$1;
			next unless ($link=~/(^\/|^\w)/);
			next if ($link=~/^\w+:/);
			if ($link=~/^\//){
				$link=$host.$link;
			}else{
				$link=$url."/".$link;
			}

			if ($link=~/(\/\s*$|\.html|\.htm)/i){
				next if (exists($visited{$link}));
				print $link,"\n";
				recursGet($ua,$link);
				
			}else{
				system("wget -4 -N -x -w 1 --limit-rate=64k -U '$agent' $link");
			}
			sleep 1;
		}
	}
}
