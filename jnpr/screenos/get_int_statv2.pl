#!/usr/bin/perl

# $Id$

#

#

use strict;
use integer;
use warnings;

my $file=shift;

my $last=0;
my $sec=0;
my $tdiff=0;
my $if;
my $inside_tfc=0;
my %if_stat;
my %tot;

unless (defined($file)){
	die "Usage:\n $0 <name of the file, with the \"get clock\" and \"get counter stat\">\n";
}


my $clock_check=0;

open(FD,$file);
while(<FD>){
	chomp;

	s/\r//g;

	if (/seconds since 1\/1\/1970/){
		$clock_check++;
		$last=$sec;	
		($sec=$_)=~s/.*?(\d+?)\..*/$1/;

		$tdiff=$sec-$last;

		my $totalinpps=0;
		my $totalinbps=0;
		my $totalinvpn=0;

		if ($last ne 0){
			foreach my $stat (%if_stat){
				$totalinpps+=$if_stat{$stat} if ($stat=~/inpackets/);
				$totalinbps+=$if_stat{$stat} if ($stat=~/inbytes/);
				$totalinvpn+=$if_stat{$stat} if ($stat=~/invpn/);
			}
			
			unless ($if_stat{"total-inpps"}==0){
				print "All interfaces in pps =\t",int(($totalinpps-$if_stat{"total-inpps"})/($tdiff)),"\n";
				$tot{"inpps"}+=($totalinpps-$if_stat{"total-inpps"});
			}

			unless ($if_stat{"total-inbps"}==0){
				print "All interfaces in bps =\t",int(($totalinbps-$if_stat{"total-inbps"})/($tdiff)),"\n";
				$tot{"inbps"}+=($totalinbps-$if_stat{"total-inbps"});
			}

			unless ($if_stat{"total-invpn"}==0){
				print "All interfaces in vpn =\t",int(($totalinvpn-$if_stat{"total-invpn"})/($tdiff)),"\n";
				$tot{"invpn"}+=($totalinvpn-$if_stat{"total-invpn"});
			}


			print "\nFor this calculation the time slot was: ",($tdiff)," seconds\n";
			$tot{"sec"}+=($tdiff);
		}
		$if_stat{"total-inpps"}=$totalinpps;
		$if_stat{"total-inbps"}=$totalinbps;
		$if_stat{"total-invpn"}=$totalinvpn;
	}
	if (/counters for interface/){
                $inside_tfc=0;
        }
	if (/Hardware counters for interface/){
		($if=$_)=~s/Hardware counters for interface (.+?):/$1/;
		$inside_tfc=1;
	}

	if ($inside_tfc==1 and /^in (packets|bytes|vpn)/){
		my $temp;
		if (/ packets /){
			($temp=$_)=~s/in packets\s+(\d+) \|.*/$1/;
			if (exists($if_stat{"$if-inpackets"})){
				my $temp1=int(($temp-$if_stat{"$if-inpackets"})/($tdiff));
				if ($temp1>0){
					print "$if in pps =\t".$temp1."\n";
				}
			}
			$if_stat{"$if-inpackets"}=$temp;
		}
		if (/ bytes /){
			($temp=$_)=~s/in bytes\s+(\d+) \|.*/$1/;
			if (exists($if_stat{"$if-inbytes"})){
				my $temp1=int(($temp-$if_stat{"$if-inbytes"})/($tdiff));
				if ($temp1>0){
					print "$if in bps =\t".$temp1."\n";
				}
			}
			$if_stat{"$if-inbytes"}=$temp;
		}
		if (/ vpn /){
			($temp=$_)=~s/in vpn\s+(\d+) \|.*/$1/;
			if (exists($if_stat{"$if-invpn"})){
				my $temp1=int(($temp-$if_stat{"$if-invpn"})/($tdiff));
				if ($temp1>0){
					print "$if in vpn =\t".$temp1."\n";
				}
			}
			$if_stat{"$if-invpn"}=$temp;
		}
	}
}
close(FD);


if ($clock_check>1){
	my $totalinpps=0;
	my $totalinbps=0;
	my $totalinvpn=0;
	foreach my $stat (%if_stat){
		$totalinpps+=$if_stat{$stat} if ($stat=~/inpackets/);
		$totalinbps+=$if_stat{$stat} if ($stat=~/inbytes/);
		$totalinvpn+=$if_stat{$stat} if ($stat=~/invpn/);
	}

	$tot{"inpps"}+=($totalinpps-$if_stat{"total-inpps"});
	$tot{"inbps"}+=($totalinbps-$if_stat{"total-inbps"});
	$tot{"invpn"}+=($totalinvpn-$if_stat{"total-invpn"});

	print "All interfaces in pps =\t",int(($totalinpps-$if_stat{"total-inpps"})/($tdiff)),"\n"   unless ($if_stat{"total-inpps"}==0);
	print "All interfaces in bps =\t",int(($totalinbps-$if_stat{"total-inbps"})/($tdiff)),"\n"   unless ($if_stat{"total-inbps"}==0);
	print "All interfaces in vpn =\t",int(($totalinvpn-$if_stat{"total-invpn"})/($tdiff)),"\n\n" unless ($if_stat{"total-invpn"}==0);

	print "\n-------------------------------\nTotal time of the file = ",$tot{"sec"}," seconds\n";
	print "Avg in pps             = ",int($tot{"inpps"}/$tot{"sec"}),"\n";
	print "Avg in bps             = ",int($tot{"inbps"}/$tot{"sec"}),"\n";
	print "Avg in vpn             = ",int($tot{"invpn"}/$tot{"sec"}),"\n";
	print "Avg pkt size           = ",int($tot{"inbps"}/$tot{"inpps"}),"\n";
}else{
	print "To few \"get clock\"s found\n";
}
