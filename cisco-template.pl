#!/usr/bin/perl -W

# Author: Marek Lukaszuk <m.lukaszuk<at>gmail.com>
# Copyright (c) 2005, Marek £ukaszuk 
# BSD License at http://monkey.geeks.pl/bsd/

use Net::Telnet::Cisco;
use MIME::Base64;
use strict;

sub timer;
my $txt;
my $ip;
my @out;


open(HOSTS,"cisco_ip.txt");
while (<HOSTS>){
	next unless ($_);
        next if (/^ *\n/);
	$ip=$_;
      	chomp;
	print ">>>>>>> $ip";
	next unless ($ip=~/(\d+\.){3}\d+/);

	@out=();

        get_cisco($ip,'user','base64_encoded_password');

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

sub get_cisco{
        # args: <adres ip cmtsa> <user> <haslo>
        my $ip=shift;
        my $user=shift;
        my $pass=shift;
	my @out;

	$pass=decode_base64($pass);

	my $cisco_template='conf t
no service pad
service nagle
service password-encryption
service timestamps log datetime localtime
service timestamps debug datetime localtime
service tcp-keepalives-in
service tcp-keepalives-out
service sequence-numbers
no service tcp-small-servers
no service udp-small-servers
ip cef
ip icmp rate-limit unreachable 200
ip icmp rate-limit unreachable DF 100
no ip http server
no ip http secure-server
no ip name-server
ip name-server 1.17.9.2 
ip domain-name it.Monkey.Mind.One.Pl
vtp domain it.Monkey.Mind.One.Pl
vtp mode transparent
ip domain-lookup
no ip source-route
no ip finger
no logging console
cdp run
no banner motd
no aaa authentication banner 
no service finger
clock timezone CET 1
clock summer-time CET recurring last Sun Mar 2:00 last Sun Oct 2:00 60
alias exec nda no deb all
alias exec siib sh ip int brief
alias exec ct conf t
alias exec sr sh run
no ntp
ntp update-calendar
ntp server 1.17.9.2
no logging
logging 1.17.9.2
logging trap informational
logging facility local7
logging history size 60
logging history warnings
snmp-server contact someone <someone@somewhere.org>
line con 0
  no logging synchronous
  exec-timeout 15 0
  exit
no line vty 16 255 
line vty 0 15
  logging synchronous
  no session-timeout
  timeout login response 60
  exec-timeout 15 0
  transport input telnet
  transport output none
  exit';


	my @cmds1=split("\n",$cisco_template);
	$cmds1[$#cmds1+1]='banner login ^ 
                *** Authorized access only ***

  This system is the property of Monkey.Mind.One.Pl 
  Disconnect IMMEDIATELY if you are not an authorised user!
  Access to this device or the attached networks is
  prohibited without express written permission.
  Violators will be prosecuted to the fullest extent of both
  civil and criminal law.
^';
	$cmds1[$#cmds1+1]='exit';
	
	my @cmds2=('undebug all','wr');

	my @cmds3=('conf t',
'no access-list 1',
'access-list 1 permit host 2.1.1.7',
'access-list 1 permit host 2.1.1.200',
'access-list 1 permit host 2.1.1.195',
'access-list 1 permit host 2.1.1.205',
'access-list 1 permit host 2.1.1.150',
'access-list 1 permit host 2.1.1.129',
'access-list 1 permit host 2.1.1.101',
'access-list 1 permit host 2.1.1.80',
'access-list 1 permit 2.1.98.0 0.0.1.255',
'access-list 1 deny any log',
'exit');

	my @cmds4=('conf t',
	'username root privilege 15 password 0 qwerty',
	'username h4x0r privilege 15 password 0 #$@RFRWR$@DAR#@R',
	'username m0nk3y privilege 15 password 0 test',
	'username tOOr privilege 15 password 0 secret',
	'exit');
	

	my @cmds5=('');

	my @cmds=@cmds2;

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
		print "$_\n";
		eval { @out = $a->cmd($_); };
		if ($@){
			print $@;
		}
		print @out;
		select(undef, undef, undef, 0.5);
	}

	$a->close;
}

