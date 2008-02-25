#!/usr/bin/perl

# Author: Marek Lukaszuk <m.lukaszuk<at>gmail.com>
# Copyright (c) 2005, Marek £ukaszuk 
# BSD License at http://monkey.geeks.pl/bsd/

use Net::Telnet::Cisco;
use MIME::Base64;
use strict;

sub timer;
my $txt;
my $ip;


open(HOSTS,"cisco_ip.txt");
while (<HOSTS>){
        next unless ($_);
        next if (/^ *\n/);
        $ip=$_;
        chomp;
      	next unless ($ip=~/(\d+\.){3}\d+/);

        docisco($ip,'user','base64_encoded_password');

}
close(HOSTS);

my $time=timer;

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

sub docisco{
        # args: <adres ip cmtsa> <user> <haslo>
        my $ip=shift;
        my $user=shift;
        my $pass=shift;
	my @out;

	$pass=decode_base64($pass);

        my $a;
        eval {  
                $a = Net::Telnet::Cisco->new(Host => $ip, Timeout => 300 );
                $a->waitfor('/(Username|Uzytkownik):/');
                $a->put("$user\n");
                $a->waitfor('/(Password|Haslo):/');
                $a->put("$pass\n");
                sleep 1;
                $a->cmd('term len 0');
        };
        return if ($@);
	
	print ">>> $ip \n";
	eval { @out = $a->cmd('sh run'); };
	print $@ if ($@);

	my $wc = chr(13);

	my $in=0;
	my $go=0;
	my $if;

	docmd($a,"conf t");
	foreach (@out){
		next unless ($_);
		s/$wc//g;
		s/\n//g;
		s/^ +//;


		
		if ($in eq "1" and /^!/){
			$in=0;
			if ($go eq "1"){
				$go=0;
				docmd($a,"$if\n");
				docmd($a,"logging event link-status");
			}
		}

		

		$go=1 if (/switchport mode trunk/);

#		if (/^line vty /){
#		if (/^crypto map .+tunnel 10 ipsec-isakmp/){
		if (/^interface .*?thernet\d+/){
#		if (/^interface Cable\d+\/\d+/){
			$in=1;
			$if=$_;
			$go=0;
#			docmd($a,$_);
#			docmd($a,"no ip redirects");
#			docmd($a,"no ip directed-broadcast");
#			docme($a,"no ip proxy-arp");
#			docmd($a,"ntp disable");
		}
		
	}
	docmd($a,"exit");
	$a->close;
}

sub docmd{
	my $a=shift;
	my $cmd=shift;

	my @shit;
	print "$cmd\n";
	eval { @shit=$a->cmd("$cmd"); }; if ($@){ print $@; }

	print @shit;
}	

