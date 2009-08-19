#!/usr/bin/perl

use strict;
use warnings;

my $file='fwry04tech0208_config';

my %serv;
my %groups;

open(FD,$file);
while(<FD>){
	chomp;
	s/(\r|\n|\0x0d)//g;

	if (/^set service .+\s+(protocol|timeout|\+)/){
		s/set service \"(.+?)\" .*/$1/;
		$serv{$_}=1;
		next;
	}	
	if (/^set group service \".+?\" add /){
		(my $grp=$_)=~s/set group service \"(.+?)\" .*/$1/;
		(my $srv=$_)=~s/set group service \".+?\" add \"(.+?)\"/$1/; 
		if (exists($groups{$grp})){
			$groups{$grp}.="|$srv";
		}else{
			$groups{$grp}="$srv";
		}
		next;
	}
	if (/^set service \".+?\"\s*/ or /^set policy id \d+ (from|name)/){

		s/set service \"(.+?)\".*/$1/ if (/^set service/);
		s/set policy id \d+ (name \".+?\"\s)?from \".+?\" to (\".+?\"\s+){3}\"(.+?)\" .*/$3/ if (/^set policy id \d+ (from|name)/);
		
		delete($serv{$_}) if (exists($serv{$_}));

		if (exists($groups{$_})){
			my @srv=split('\|',$groups{$_});
			foreach my $srv1 (@srv){
				delete($serv{$srv1}) if (exists($serv{$srv1}));
			}
			delete($groups{$_});
		}
	}
}
close(FD);


foreach my $key (keys %serv){
	print "$key\n";
}

foreach my $key (keys %groups){
        print "$key\n";
}

