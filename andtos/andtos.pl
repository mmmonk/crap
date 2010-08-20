#!/usr/bin/perl -wW

# Active Network Discovery Tool Over SNMP
# Author <m.lukaszuk@gmail.com> 2005
# $Id$

require v5.6.1;

BEGIN {
	if (eval "use Net::SNMP"){
		die "you don't have Net::SNMP library, you can download it from http://cpan.org\n";
	}
	if (eval "use Getopt::Std"){
		die "you don't have Getopt::Std library, you can download it from http://cpan.org\n";
	}

	if (eval "use Digest::MD5"){
		die "you don't have Digest::MD5 library, you can download it from http://cpan.org\n";
	}
}

use strict;
use integer;

my %args=();
getopt("vh",\%args);

my $maindir	= "andtos";
my $outtime	= timer(); # current time
my $outfile	= "$maindir/andtos.$outtime.txt";
my $savedir	= "andtos.save";


### what IP to include in the search
my @include     = ('192\.168\.\d+\.\d+','172\.\d+\.\d+\.\d+','10\.50\.\d+\.\d+');

### SMNP variables
my $snmpfile	= "andtos.snmp";
my @snmpcom 	= ('public','private');
my %snmpcomtmp	= (); # variable needed for sorting snmp password 

my $OIDtest     = '1.3.6.1.2.1.1.1.0';
my $OIDrdest    = '1.3.6.1.2.1.4.21.1';
my $OIDnet2med  = '1.3.6.1.2.1.4.22.1';
my $OIDmyipaddr = '1.3.6.1.2.1.4.20.1.1';

my %found=();

my $host=shift;
unless ($host){
	die "$0 <seed_ip>\n";
}

# reading snmp strings from file
if( -f $snmpfile){
	open(SNMP,$snmpfile);
	while(<SNMP>){
		chomp;
		push(@snmpcom,$_);
	}
	close(SNMP);
}

mkdir($maindir,0700);
mkdir($savedir,0700);

map($snmpcomtmp{$_}=0,@snmpcom);

hostconn('1',$host);

#### main proc ####
sub hostconn{
	my $seed=shift;
	my $mhost=shift;

	my ($session, $error, $child, $commstr, $snmpok, %print, @kids, @myaddr, @connected, $savefile);
	$snmpok=0;
	@myaddr=();
	@connected=();

	# sorting community strings
	@snmpcom=sort{$snmpcomtmp{$b} <=> $snmpcomtmp{$a}} keys %snmpcomtmp;

	foreach my $snmpcomm (@snmpcom){
		($session,$error)  = Net::SNMP->session(
			-timeout        => 3,
			-retries        => 3,
			-hostname       => $mhost,
			-community      => $snmpcomm,
			-port           => 161,
			-version        => "snmpv2c"
		); 
		
		if (defined($session)){
			my $tre=$session->get_request(-varbindlist => ["$OIDtest"]);
			if (defined($tre)){
				$snmpok=1;
				$commstr=$snmpcomm;
				die "error in community snmp hash for value: $snmpcomm\n" unless (exists($snmpcomtmp{$snmpcomm}));
				$snmpcomtmp{$snmpcomm}++;
				last;
			}else{
				$session->close;
			}
		}
	}

	print "[$mhost]\n";

	unless ($snmpok==0){

		# pobranie adresow IP z urzadzenia i dodanie ich do %found
		#
		my $req = $session->get_table( -baseoid => $OIDmyipaddr );
		if ($req){
			foreach my $ent (sort snmplastoid keys %$req){
				next unless ($req->{$ent});
				$myaddr[$#myaddr+1]=$req->{$ent};
				$found{$req->{$ent}}=1;
			}
		}	

		if ($seed == 1){
                        $savefile="$savedir/seed";
                }else{          
                        @myaddr=sort(@myaddr);
                        my $md5 = Digest::MD5->new;
                        $md5->add(join('',@myaddr));    
                        $savefile="$savedir/".$md5->b64digest;
                }               
	

	
		# pobranie wpisow z tabeli routingu, interesuja
		# nas gatewaye jako sasiedzi
		$req = $session->get_table( -baseoid => $OIDrdest.".7" );
		if ($req){
			foreach my $ent (sort snmplastoid keys %$req){
				next unless ($req->{$ent});			
				my $nexthost=$req->{$ent};
				
				if (add2connected($nexthost)){
					$connected[$#connected+1]=$nexthost;
				}
			}
		}

		# pobranie wpisow IP z tablicy ARP
		# 
		$req = $session->get_table( -baseoid => $OIDnet2med.".3" );
		if ($req){
	
			foreach my $ent (sort snmplastoid keys %$req){
				next unless ($req->{$ent});
				my $nexthost=$req->{$ent};

				if (add2connected($nexthost)){
					$connected[$#connected+1]=$nexthost;
				}
			}
		}

		open(FD,">> $outfile");
		print FD "$mhost;";
		foreach my $get (@myaddr){
			print FD "$get ";
		}

		open(HOST,"> $maindir/$mhost"."_.txt");
		print HOST "snmpcomm: $commstr\n";
		my @text=getsystem($session);
		print HOST @text;


		unless ($child = fork){
			die "cannot fork: $!" unless defined $child;

			open(INTCSV,"> $maindir/$mhost"."_if.csv");	
			@text=getinterface($session);
			print INTCSV @text;
			close(INTCSV);

			open(RCSV,"> $maindir/$mhost"."_r.csv");
			@text=getrouting($session);
			print RCSV @text;
			close(RCSV);
		
			$session->close;
			exit;
		}
		push(@kids,$child);
		
		$session->close;
	
		print HOST "---------------------------\n";
		print FD ";";	
		foreach my $get (@connected){
			print FD "$get ";
			print HOST "$get\n";
		}
		print FD "\n";
		close(FD);	
		close(HOST);

		# save current state
		
#		print "save - $savefile\n";
	
		foreach my $get (@connected){
			next if ($get=~/^172\.19\.\d+\.\d+/);
			hostconn('0',$get);
		}
	}
}


############################################# Procedury

# test czy dodac host do @connected, oraz dodanie do %found 
sub add2connected{
	my $tmphost=shift;
	my $exchost=0;

	unless (exists($found{$tmphost})){
		$found{$tmphost}=1;

		foreach my $exctest (@include){
			if ($tmphost=~/$exctest/){
				$exchost=1;
				last;
			}
		}
	}

	return $exchost;
}


# funkcja do sort'u, do sortowania oidow
sub snmplastoid{
	(my $a1 = $a)=~s/.*?\.(\d+)$/$1/;
	(my $b1 = $b)=~s/.*?\.(\d+)$/$1/;

	$a1 <=> $b1;
}


# konwersja MAC do noramlnego textu
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

# pobieram spis interfejsow wraz z adresacja - RFC 1213,
sub getinterface{
	my $newsess=shift;

	my $OIDif               = '1.3.6.1.2.1.2.2.1';
	my $OIDifindex          = $OIDif.'.1';
	my $OIDipAdEntIfIndex   = '1.3.6.1.2.1.4.20.1.2';
	my $OIDipAdEntNetMask   = '1.3.6.1.2.1.4.20.1.3';

	my @out=();

	my %ifstatus    = (
		1 => "up",
		2 => "down",
		3 => "other",
		4 => "unknown",
		5 => "dormant"
	);

	my %iftype      = (
		1 => "other",
		6 => "ethernetCsmacd",
		18 => "ds1",
		22 => "propP2PSerial",
		23 => "ppp",
		24 => "softLoopback",
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

	push(@out,"Descr;Type;MTU;Speed;MAC;Admin;Oper;\n");

        my $req = $newsess->get_table( -baseoid => $OIDipAdEntIfIndex );
        return unless ($req);

        my $re = $newsess->get_table( -baseoid => $OIDifindex );
        if ($re){
                foreach (sort snmplastoid keys %$re){
                        next unless ($_);
                        (my $loid=$_)=~s/.*?\.(\d+)$/$1/;
                        
                        my $re2=rowget($newsess,$OIDif,$loid,2,8);

                        my $text="";
                        for (my $i=2; $i <=8; $i++){
                                my $value=$re2->{"$OIDif.$i.$loid"};

                                $value=$ifstatus{$value} if ($i==7 or $i==8);
				$value=$iftype{$value} if ($i==3);
                                $value=0 if ($i==4 and $value eq "noSuchInstance");
                                $value=convmac($value) if ($i==6);
 
				if ($i==3){
                                        my $ipaddr="";
                                        foreach my $tmpoid (keys %$req){
                                                next unless ($tmpoid);
                                                ($ipaddr=$tmpoid)=~s/.*?\.(\d+\.\d+\.\d+\.\d+)$/$1/;
                                                next if ($req->{$tmpoid} ne $loid);
                                                if ($ipaddr=~/\d+\.\d+\.\d+\.\d+$/){
                                                        my $netmask=$newsess->get_request( -varbindlist => [ "$OIDipAdEntNetMask.$ipaddr" ]);
                                                        if ($netmask){
                                                                $text.="$ipaddr/".$netmask->{"$OIDipAdEntNetMask.$ipaddr"}." ";
                                                        }else{
                                                                $text.="$ipaddr/,";
                                                        }
                                                }
                                        }
                                        $text.=";";

                                }
                                
				if ($i==5){
                                        $value=$value/1024;
                                        if ($value > 1024){
                                                $value=($value/1024)." Mb/s";
                                        }else{
                                                $value="$value Kb/s";
                                        }
                                }
                                $text.="$value;";
                        }
                        push(@out,"$text\n");
		}
	}
	return @out;
}


# opis system
sub getsystem{
	my $newsess=shift;

	my @out=();

	my $OIDsystem   = '1.3.6.1.2.1.1';

	my $req = $newsess->get_table( -baseoid => $OIDsystem);
	if ($req){
		foreach my $ent (sort snmplastoid keys %$req){
			next unless ($req->{$ent});
			push(@out,"$ent -> ".$req->{$ent}."\n");
		}
	}
	return @out;
}

# tablica routingu - RFC 1213 
sub getrouting{
	my $newsess=shift;

	my @out=();

	my $OIDroute	= '1.3.6.1.2.1.4.21.1';

	my %prototype = (
		1 => "other",   
		2 => "local",   
		3 => "netmgmt", 
		4 => "icmp",    
		5 => "egp",     
		6 => "ggp",     
		7 => "hello",   
		8 => "rip",     
		9 => "isIs",    
		10 => "esIs",   
		11 => "ciscoIgrp",
		12 => "bbnSpfIgp",
		13 => "ospf",   
		14 => "bgp",    
		15 => "idpr",   
		16 => "ciscoEigrp"
	);

	my %routetype = (
		1 => "other",
		2 => "invalid",
		3 => "direct",
		4 => "indirect",
	);

	push(@out,"Dest;IfIndex;Metric1;Metric2;Metric3;Metric4;NextHop;Type;Proto;Age;Mask;Metric5;Info\n");
	my $re = $newsess->get_table( -baseoid => $OIDroute.".1");
        if ($re){
                foreach (sort snmplastoid keys %$re){
                        next unless ($_);
                        (my $loid=$_)=~s/.*?\.(\d+\.\d+\.\d+\.\d+)$/$1/;

			my $text=$re->{$_}.";";
                        my $re2=rowget($newsess,$OIDroute,$loid,2,13);
			for (my $i=2; $i <=13; $i++){
				my $value=$re2->{"$OIDroute.$i.$loid"};
				$value=$routetype{$value} if($i==8 and exists($routetype{$value}));
				$value=$prototype{$value} if($i==9 and exists($prototype{$value}));
				$value="" if ($value eq '-1');
				$text.=$value.";";
			}
			next if ($text=~/;bgp;/); # niechcemy zapisywac calej tablicy BGP ;)
			$text.="\n";
			push(@out,$text);
		}
	}
	return @out;
}

# uproszczenie pobrania jednej linijki z tabeli po snmp
sub rowget {
    my $session = shift;
    my $OIDmain = shift;
    my $OIDend  = shift;
    my $cstart  = shift;
    my $cend    = shift;
    
    my $tmpre;
    my $tquery = '$tmpre=$session->get_request(-varbindlist=>[';
    for ( my $counter = $cstart ; $counter <= $cend ; $counter++ ) {
        $tquery .= "'$OIDmain.$counter.$OIDend'";
        $tquery .= "," if ( $counter < $cend );
    }
    $tquery .= "]);";

    eval $tquery;
    print $@ if ($@);

    return $tmpre;
}


# formatowanie czasu
sub timer{
	my ($sec,  $min,  $hour,  $mday,  $mon,  $year);
	($sec,$min,$hour,$mday,$mon,$year,undef,undef,undef) = localtime(time);
	$year+= 1900;$mon+=1;       
	$hour="0$hour" if $hour < 10;
	$mday="0$mday" if $mday < 10;
	$mon="0$mon" if $mon < 10;  
	$min="0$min" if $min < 10;  
	$sec="0$sec" if $sec < 10;  
	my $ret=$year.$mon.$mday.$hour.$min.$sec;
	return $ret;                
}

sub REAPER {
    my $stiff;
    while (($stiff = waitpid(-1, &WNOHANG)) > 0) {
        # do something with $stiff if you want
    }
    $SIG{CHLD} = \&REAPER;                  # install *after* calling waitpid
}



# process handlers 
#$SIG{INT}  = sub { die "$$ dying\n" };
$SIG{CHLD} = 'IGNORE';
#$SIG{CHLD} = \&REAPER; 
