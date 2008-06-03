#!/usr/bin/perl

#
# Author: mlukaszuk@juniper.net
#

use strict;

my $file=shift;

my $last=0;
my $sec=0;
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

		my $totalinpps=0;
		my $totalinbps=0;
		if ($last ne 0){
			foreach my $stat (%if_stat){
				$totalinpps+=$if_stat{$stat} if ($stat=~/inpackets/);
				$totalinbps+=$if_stat{$stat} if ($stat=~/inbytes/);
			}

			
			unless ($if_stat{"total-inpps"}==0){
				print "All interfaces in pps =\t",int(($totalinpps-$if_stat{"total-inpps"})/($sec-$last)),"\n";
				$tot{"inpps"}+=($totalinpps-$if_stat{"total-inpps"});
			}

#			unless ($if_stat{"total-inbps"}==0){
#				print "All interfaces in bps =\t",int(($totalinbps-$if_stat{"total-inbps"})/($sec-$last)),"\n\n";
#				$tot{"inbps"}+=($totalinbps-$if_stat{"total-inbps"});
#			}

			print "For this calculation the time slot was: ",($sec-$last)," seconds\n";
			$tot{"sec"}+=($sec-$last);
		}
		$if_stat{"total-inpps"}=$totalinpps;
		$if_stat{"total-inbps"}=$totalinbps;
	}
	if (/counters for interface/){
                $inside_tfc=0;
        }
	if (/Hardware counters for interface/){
		($if=$_)=~s/Hardware counters for interface (.+?):/$1/;
		$inside_tfc=1;
	}

	if ($inside_tfc==1 and /^in (packets|bytes)/){
		my $temp;
		if (/ packets /){
			($temp=$_)=~s/in packets\s+(\d+) \|.*/$1/;
			if (exists($if_stat{"$if-inpackets"})){
				my $pps=int(($temp-$if_stat{"$if-inpackets"})/($sec-$last));
				if ($pps>0){
					print "$if in pps =\t".$pps."\n";
				}
			}
			$if_stat{"$if-inpackets"}=$temp;
		}
		if (/ bytes /){
			($temp=$_)=~s/in bytes\s+(\d+) \|.*/$1/;
			if (exists($if_stat{"$if-inbytes"})){
				my $bps=int(($temp-$if_stat{"$if-inbytes"})/($sec-$last));
				if ($bps>0){
#					print "$if in bps =\t".$bps."\n";
				}
			}
			$if_stat{"$if-inbytes"}=$temp;
		}
	}
}
close(FD);


if ($clock_check>1){
	my $totalinpps=0;
	my $totalinbps=0;
	foreach my $stat (%if_stat){
		$totalinpps+=$if_stat{$stat} if ($stat=~/inpackets/);
		$totalinbps+=$if_stat{$stat} if ($stat=~/inbytes/);
	}

	$tot{"inpps"}+=($totalinpps-$if_stat{"total-inpps"});
	$tot{"inbps"}+=($totalinbps-$if_stat{"total-inbps"});

	print "All interfaces in pps =\t",int(($totalinpps-$if_stat{"total-inpps"})/($sec-$last)),"\n";
	#print "All interfaces in bps =\t",int(($totalinbps-$if_stat{"total-inbps"})/($sec-$last)),"\n\n";

	print "Total time of the file = ",$tot{"sec"}," seconds\n";
	print "Avg in pps             = ",int($tot{"inpps"}/$tot{"sec"}),"\n";
	#print "Avg in bps             = ",int($tot{"inbps"}/$tot{"sec"}),"\n";
	#print "Avg pkt size           = ",int($tot{"inbps"}/$tot{"inpps"}),"\n";
}else{
	print "To few \"get clock\"s found\n";
}
