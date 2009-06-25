#!/usr/bin/perl -w

# Author: Marek Lukaszuk <m.lukaszuk<at>gmail.com>
# Copyright (c) 2005, Marek £ukaszuk 
# BSD License at http://monkey.geeks.pl/bsd/

use Net::SNMP;
use Rcs;
use strict;
use integer;

my $OIDif 		= '1.3.6.1.2.1.2.2.1';
my $OIDifindex 		= $OIDif.'.1';
my $OIDipAdEntIfIndex 	= '1.3.6.1.2.1.4.20.1.2';
my $OIDipAdEntNetMask	= '1.3.6.1.2.1.4.20.1.3';
my $OIDsyshostname	= '1.3.6.1.2.1.1.5.0';
my $OIDserialnumber	= '1.3.6.1.4.1.9.3.6.3.0';

my $sendmail="/usr/lib/sendmail";
my $maindir="/home/user/if-ip-diff";
my $txt="";

Rcs->quiet(1);
my $rcs = Rcs->new;
$rcs -> bindir('/usr/local/bin');
$rcs -> rcsdir("$maindir/arch");
$rcs -> workdir("$maindir/current");

my $snmpcomm='secretpassword';

my %ifstatus    = (
	1 => "up",
	2 => "down",
	3 => "other",
	4 => "unknown",
	5 => "dormant"
);

my %iftype	= (
	1 => "other",
	5 => "rfc877x25",
	6 => "ethernetCsmacd",
	18 => "ds1",
	22 => "propP2PSerial",
	23 => "ppp",
	24 => "softLoopback",
	28 => "slip",
	32 => "frameRelay",
	37 => "atm",
	39 => "sonet",
	49 => "aal5",
	53 => "propVirtual",
	63 => "isdn",
	75 => "isdns",
	77 => "lapd",
	81 => "ds0",
	101 => "voiceFXO",
	103 => "voiceEncap",
	104 => "voiceOverIp",
	117 => "gigabitEth",
	127 => "docsCMac",
	128 => "docsCDown",
	129 => "docsCUp",
	131 => "tunnel",
	134 => "atmSubIf",
	135 => "l2vlan",
	171 => "PacketOverSONET"
);

open(HOSTS,"$maindir/dev.txt");
open(FD,"> $maindir/current/if_snmp.txt");

print FD "Host;Hostname;Serial;Descr;IPAddr;Type;MTU;Speed;MAC;Admin;\n";
while (<HOSTS>){
	next unless ($_);
	next if (/^ *\n/);
	chomp;
	my $host=$_;
	next unless ($host=~/(\d+\.){3}\d+/);

#	next if ($host ne "192.168.111.1");

#	print "[+] $host\n";

	my ($session, $error) = Net::SNMP->session(
		-timeout        => 10,
		-retries        => 5,
		-hostname       => $host,
		-community      => $snmpcomm,
		-port           => 161,
		-version        => 2,
		-translate      => 1
	);

	if (!defined($session)){
		$session->close;
		next;
	}
	
	my $req = $session->get_table( -baseoid => $OIDipAdEntIfIndex );
	next unless ($req);

	my $req1 = $session->get_request( -varbindlist => [ $OIDsyshostname,$OIDserialnumber ]);
	my $hostname="";
	my $serialnum="";
	if ($req1){
		$hostname=$req1->{$OIDsyshostname};
		$serialnum=$req1->{$OIDserialnumber};
	}

	my $re = $session->get_table( -baseoid => $OIDifindex );
	if ($re){
		foreach (sort snmplastoid keys %$re){
			next unless ($_);
			(my $loid=$_)=~s/.*?\.(\d+)$/$1/;
			
			my $re2;
			my $question='$re2 = $session->get_request( -varbindlist => [ ';
			for (my $i=2; $i <=8; $i++){
				$question.="'$OIDif.$i.$loid'";
				$question.=", " unless ($i==8);
			}
			$question.=" ]);";
			
			eval $question;
			print $@ if ($@);
			my $text="";
			for (my $i=2; $i <=7; $i++){
				my $value=$re2->{"$OIDif.$i.$loid"};
				$value=$ifstatus{$value} if ($i==7 or $i==7);
				if ($i==3){
					my $ipaddr="";	
					foreach my $tmpoid (keys %$req){
						next unless ($tmpoid);
						($ipaddr=$tmpoid)=~s/.*?\.(\d+\.\d+\.\d+\.\d+)$/$1/;
						next if ($req->{$tmpoid} ne $loid);
						if ($ipaddr=~/\d+\.\d+\.\d+\.\d+$/){
							my $netmask=$session->get_request( -varbindlist => [ "$OIDipAdEntNetMask.$ipaddr" ]);
							if ($netmask){
								$text.="$ipaddr/".$netmask->{"$OIDipAdEntNetMask.$ipaddr"}." ";
							}else{
								$text.="$ipaddr/,";
							}
						}
					} 
					$text.=";";
				
				}
				if ($i==3){
					if (exists($iftype{$value})){
						$value=$iftype{$value};
					}else{
						print "$host - iftype $value doesn't exists\n";
					}
				}
				if ($i==4){
					$value=0 if ($value eq "noSuchInstance");
				}
				if ($i==6){
					$value=convmac($value);
				}
				if ($i==5){
					$value=$value/1000;
					if ($value > 1000){
						
						$value=($value/1000)." Mb/s";
					}else{
						$value="$value Kb/s";
					}
				}	
				$text.="$value;";
			}
			print FD "$host;$hostname;$serialnum;$text\n";
		}
	}
	$session->close;
}
close(FD);
close(HOSTS);

$rcs -> file("if_snmp.txt");
my $time=timer();
unless (open(FD,"$maindir/arch/if_snmp.txt,v")){
	$rcs -> ci('-l',"-m$time","-t-\".\"");
	close(FD);
	exit;
}

if ($rcs -> rcsdiff) {
	my $tmptxt="";
	my $triger=0;
	my $count=0;
	foreach my $l ($rcs -> rcsdiff){
		unless ($l=~m/^[<>\-\n]/){
			$l="\n";
		}
		if ($l=~/^\n/){
			$triger=0;
			$count=0;
		}

		$count++ if ($triger != 0);

		next if ($count == 1 and $l=~/^---\n/);
		next if (($l=~/^---\n/ or $l=~/^\n/) and $tmptxt eq "");
		
		$l=~s/^</rem:/;
		$l=~s/^>/add:/;

		if ($l=~/(switch|192\.168\.\d+\.5|192\.168\.\d+\.6)/i){
			$triger=1;
			next;
		}
		$tmptxt.=$l;
	}

	$rcs -> ci('-l',"-m$time");
	$txt.=$tmptxt;
}

exit if ($txt eq "");

my $msg="To: <abuse\@microsoft.com>
Content-Type: text/plain;
        charset=\"iso-8859-2\"
From: Watcher <somone\@somewhere.banana>
Subject: [IFIP] Raport zmian w stanie interfejsów z $time

$txt

";     

open(SENDMAIL,"| $sendmail -oi -t ") or die "Nie mogê otworzyæ sendmail'a: $!\n";
print SENDMAIL $msg;
close(SENDMAIL) or warn "Sendmail nie zamkn±³ siê ³adnie: $!\n";


sub convmac{
        my $badmac=shift;
        my @tmp;
        my $i=0;
	my $newmac;
        if ($badmac=~/^0x.+/){
		$badmac=~s/0x//;
		$newmac=$badmac;
	}else{
		foreach (split('',$badmac)){
                	my $c=sprintf("%2x",ord($_));
                	$c=~s/ /0/;
                	$tmp[$i++]=$c;
        	}
        	$newmac=join('',@tmp);
        }	
	return $newmac;
}

sub snmplastoid{
	(my $a1=$a)=~s/.*?\.(\d+)$/$1/;
	(my $b1=$b)=~s/.*?\.(\d+)$/$1/;

	$a1 <=> $b1;
}

sub timer{
    my $sec; my $min; my $hour; my $mday; my $mon; my $year;
    ($sec,$min,$hour,$mday,$mon,$year,undef,undef,undef) = localtime(time);
    $year+= 1900;$mon+=1;
    $hour="0$hour" if $hour < 10;
    $mday="0$mday" if $mday < 10;
    $mon="0$mon" if $mon < 10;
    $min="0$min" if $min < 10;
    $sec="0$sec" if $sec < 10;
    my $ret=$year."-".$mon."-".$mday."_".$hour.":".$min.":".$sec;
    return $ret;
}       

