#!/usr/bin/perl -W

# $Id$





use Net::Telnet::Cisco;
use MIME::Base64;
use strict;

sub timer;
my $txt;
my $ip;
my @out;


my $logserver='192.168.0.1';

open(HOSTS,"cisco_ip.txt");
while (<HOSTS>){
	next unless ($_);
        next if (/^ *\n/);
	chomp;
	$ip=$_;
	next unless ($ip=~/(\d+\.){3}\d+/);

	@out=();

	print ">>>>>>> $ip\n";       
        docisco($ip,'user','base64_encoded_password');

}
close(HOSTS);

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

sub docisco {
        # args: <adres ip cmtsa> <user> <haslo>
        my $ip=shift;
        my $user=shift;
        my $pass=shift;
	my @out;

	$pass=decode_base64($pass);

	my @c1=(
'conf t',
'no service pad',
'no service config',
'service nagle',
'service password-encryption',
'service timestamps log datetime localtime',
'service timestamps debug datetime localtime',
'service tcp-keepalives-in',
'service tcp-keepalives-out',
'service sequence-numbers',
#'aaa new-model',
#'aaa authentication login default local-case',
#'aaa authentication login con local-case',
#'aaa authentication ppp default local',
#'aaa authorization console',
#'aaa authorization exec default local',
#'aaa authorization network default local',
'no service tcp-small-servers',
'no service udp-small-servers',
'ip cef',
'ip icmp rate-limit unreachable 200',
'ip icmp rate-limit unreachable DF 100',
'no ip http server',
'no ip http secure-server',
'no ip name-server',
"ip name-server $logserver",
'ip domain-name noc.monkey.mind.one.pl',
'ip domain-lookup',
'no ip source-route',
'no ip finger',
'no logging console',
'no cdp run',
'no banner motd',
'no aaa authentication banner ',
'no service finger',
'clock timezone CET 1',
'clock summer-time CET recurring last Sun Mar 2:00 last Sun Oct 2:00 60',
'alias exec nda no deb all',
'alias exec siib sh ip int brief',
'alias exec ct conf t',
'alias exec sr sh run',
'no ntp',
"ntp server $logserver",
'ntp update-calendar',
"logging $logserver",
'logging trap informational',
'logging facility local7',
'logging history size 60',
'logging history warnings',
'snmp-server contact NOC <noc@monkey.mind.one.pl>',
'snmp-server community verysecretpassword RO 13',
'no snmp-server enable traps',
'line con 0',
#'  login authentication con',
'  login local',
'  transport input none',
'  transport output none',
'  transport preferred none',
'  logging synchronous',
'  exec-timeout 15 0',
'no line vty 16 255',
'interface Null0',
'  no ip unreachables');

	push(@c1,'banner login ^ 
                *** Authorized access only ***

  This system is the property of Monkey.Mind.One.Pl
  Disconnect IMMEDIATELY if you are not an authorised user!
  Access to this device or the attached networks is
  prohibited without express written permission.
  Violators will be prosecuted to the fullest extent of both
  civil and criminal law.
^');
	if ($ip=~/\d+\.\d+\.\d+\.(129|130|150)/){
		push(@c1,'alias exec scmst sh cable modem s t');
		push(@c1,'alias exec scm sh cable modem');
		push(@c1,'alias exec scmr sh cable modem remot');
		push(@c1,'privilege interface level 14 cablelength');
		push(@c1,'privilege interface level 14 cable upstream');
		push(@c1,'privilege interface level 14 cable downstream');
		push(@c1,'privilege interface level 14 cable');
		push(@c1,'privilege interface level 14 ip helper-address');
		push(@c1,'privilege interface level 14 ip address');
		push(@c1,'privilege interface level 14 ip');
		push(@c1,'privilege configure level 14 interface');
		push(@c1,'privilege exec level 14 show cable modem');
		push(@c1,'privilege exec level 14 show cable qos profile');
		push(@c1,'privilege exec level 14 show cable qos');
		push(@c1,'privilege exec level 14 show cable');
		push(@c1,'privilege exec level 14 show controllers');
		push(@c1,'privilege exec level 14 show interfaces Cable2/0 modem');
		push(@c1,'privilege exec level 14 show interfaces');
		push(@c1,'privilege exec level 14 show running-config');
		push(@c1,'privilege exec level 14 show');
		push(@c1,'privilege exec level 14 clear cable modem');
		push(@c1,'privilege exec level 14 clear cable');
		push(@c1,'privilege exec level 14 clear');
	
	}
	push(@c1,'exit');

#	my @c2=('sh debug','undebug all','wr');
		
	my @cmds=@c1;

        my $a;
        eval {  
                $a= Net::Telnet::Cisco->new(Host => $ip, Timeout => 300 );
                unless ($a->login($user,$pass)){
                        print "ERROR: $!\n kontakt z $ip\n";
                        return;
                }
	};
	return if ($@);
	
	foreach (@cmds){
		print ">>> $ip - $_\n";
		eval { @out = $a->cmd($_); }; if ($@){ print $@; }
		
		print @out;
		select(undef, undef, undef, 0.5);
	}

	eval { @out = $a->cmd('sh run'); }; if ($@){ print $@; }

	
	my $wc = chr(13);
	docmd($a,"conf t");
	foreach (@out){
		next unless ($_);
		s/$wc//g;
		s/\n//g;
		s/^ +//;
		if (/^interface Cable\d+\/\d+/){	
			docmd($a,$_);
			docmd($a,"cable source-verify");
			docmd($a,"cable tftp-enforce");
			docmd($a,"ip route-cache flow");
			docmd($a,"ntp disable");
			docmd($a,"no keepalive");
			docmd($a,"no cable ip-multicast-echo");
			docmd($a,"exit");
		}
		if (/^line vty /){
			docmd($a,$_);
			docmd($a,"login local");
			docmd($a,"");
			docmd($a,"logging synchronous");
			docmd($a,"exec-timeout 15 0");
			docmd($a,"timeout login response 60");
			docmd($a,"transport input telnet");
			docmd($a,"transport output telnet");
			docmd($a,"exit");
		}
	}
	docmd($a,"exit");
	$a->close;
}

sub docmd{
	my $a=shift;
	my $cmd=shift;

	my @outc;
	print "$cmd\n";
	eval { @outc=$a->cmd("$cmd"); }; if ($@){ print $@; }
	print @outc;
}

