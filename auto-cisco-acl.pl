#!/usr/bin/perl -W

# Author: Marek Lukaszuk <m.lukaszuk<at>gmail.com>
# Copyright (c) 2005, Marek £ukaszuk 
# BSD License at http://monkey.geeks.pl/bsd/

use Net::Telnet::Cisco;
use Net::Netmask;
use MIME::Base64;
use strict;

sub timer;
my $txt;
my $ip;
my @out;


my $aclname="test_in";

open(HOSTS,"cisco_ip.txt");
while (<HOSTS>){
	next unless ($_);
        next if (/^ *\n/);
	chomp;
	$ip=$_;
      	next unless ($ip=~/(\d+\.){3}\d+/);

	@out=();

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

	my @smtpboys=();
	my @localnets=();
	my @localaddr=();
	my @localbrod=();
	my $prim="";
	
	my @acl=();
	
        my $a;
        eval {  
                $a= Net::Telnet::Cisco->new(Host => $ip, Timeout => 300 );
                unless ($a->login($user,$pass)){
                        print "ERROR: $!\n kontakt z $ip\n";
                        return;
                }
        };
        return if ($@);
	
	print ">>> $ip \n";
	eval { @out = $a->cmd("sh access-list $aclname"); };
	if ($@){ print $@; }

	my $wc = chr(13);

	my $smtpdeny=0;	
	foreach (@out){
		s/$wc//g;
		s/\n//g;
		s/^ +//;
		next unless ($_);
		$smtpdeny=1 if (/deny +tcp any eq smtp any/);
		next unless (/permit .+ smtp/);

		s/ \(\d+ match.*?\)//;
		s/^\d+ //;

		push(@smtpboys,$_);
	
	}

	eval { @out = $a->cmd('sh run'); };
        if ($@){ print $@; }
	
	my $aclinter;
        my $aclon=0;
        my $tmpinter;
	my $incable=0;
	foreach (@out){
		s/$wc//g;
		s/\n//g;
		s/^ +//;
		next unless ($_);

		$incable=0 if(/^interface /);
		$incable=1 if(/^interface Serial/);
		
		if ($incable==1 and /^ip address \d+/){
			$aclinter=$tmpinter;
			s/ip address //;
			unless (/ secondary/){	
				$prim=(split(" ",$_))[0];
			}
			s/ secondary//;
			my @ipcab=split(" ",$_);
			my $nipcab=new Net::Netmask("$ipcab[0]:$ipcab[1]");
			
			unless (/^10\.\d+\./){
				push(@localnets,$nipcab->base()." ".$nipcab->hostmask());
			}
			
			push(@localaddr,$ipcab[0]);
			push(@localbrod,$nipcab->broadcast());
		}
	}

	my $acl_temp="no ip access-list extended $aclname 
ip access-list extended $aclname 
 remark ----- DENY MULTICAST -----
 deny   ip any 224.0.0.0 0.255.255.255";
	@acl=split("\n",$acl_temp);

	
	push(@acl," remark ----- INTERFACE ADDRESSES -----");
	foreach my $line (@localaddr){
		if($line eq $prim){
			push(@acl," permit udp 10.0.0.0 0.255.255.255 host $line eq 69");
			push(@acl," permit udp 10.0.0.0 0.255.255.255 eq 161 host $line gt 1024");
			push(@acl," permit icmp any host $line echo-reply");
		}
		push(@acl," deny   ip  any host $line");
	}
#	foreach my $line (@localbrod){
#		push(@acl," deny   ip  any host $line");
#	}

	if($smtpdeny==1){
		push(@acl," remark ----- SMTP FILTER -----");
		foreach my $line (@smtpboys){
			push(@acl," $line");
		}
		push(@acl," deny   tcp any eq smtp any");
	}
	
	push(@acl," remark ----- PRIVATE ADDRESSES  -----");
	push(@acl," permit udp any eq 68 192.168.0.225 0.0.255.0 eq 67");
	push(@acl," permit udp any eq 68 192.168.0.226 0.0.255.1 eq 67");
	push(@acl," permit udp any eq 68 192.168.0.228 0.0.255.0 eq 67");
	foreach my $line (@localnets){
		push(@acl," deny   ip $line 192.168.0.0 0.0.255.255");
	}
	foreach my $line (@localnets){
		if ($line=~/^172\.19\./){
			 push(@acl," permit ip $line $line");
		}
		push(@acl," deny   ip $line 172.16.0.0 0.3.255.255");
	}
	foreach my $line (@localnets){
		push(@acl," permit ip $line any");
	}

	push(@acl," permit icmp any 192.168.0.0 0.0.255.255 echo-reply");
	push(@acl," permit icmp any 172.20.0.0 0.0.255.255 echo-reply");
	push(@acl," permit udp 10.0.0.0 0.255.255.255 eq 161 172.20.0.0 0.0.255.255 gt 1024");
	
	push(@acl," permit udp 10.0.0.0 0.255.255.255 gt 1024 192.168.0.225 0.0.255.0 eq 69");
        push(@acl," permit udp 10.0.0.0 0.255.255.255 gt 1024 192.168.0.225 0.0.255.0 eq 37");
        push(@acl," permit udp 10.0.0.0 0.255.255.255 gt 1024 192.168.0.225 0.0.255.0 eq 514");
        push(@acl," permit udp 10.0.0.0 0.255.255.255 gt 1024 192.168.0.225 0.0.255.0 eq 53");
        push(@acl," permit udp 10.0.0.0 0.255.255.255 gt 1024 192.168.0.225 0.0.255.0 eq 162");
        push(@acl," permit udp 10.0.0.0 0.255.255.255 eq 161 192.168.0.225 0.0.255.0 gt 1024");
        push(@acl," permit udp 10.0.0.0 0.255.255.255 gt 1024 192.168.0.225 0.0.255.0 gt 1024");

	push(@acl," permit udp 10.0.0.0 0.255.255.255 192.168.4.0 0.0.3.255");
	push(@acl," permit ip 10.0.0.0 0.255.255.255 192.168.106.0 0.0.0.255");
	push(@acl," permit ip 10.0.0.0 0.255.255.255 192.168.1.0 0.0.0.255");
	push(@acl," permit ip 10.0.0.0 0.255.255.255 192.168.111.0 0.0.0.255");
	push(@acl," permit udp host 0.0.0.0 eq 68 host 255.255.255.255 eq 67");
	push(@acl," deny   ip any any");

	docmd($a,"conf t");
	if ($aclon==1){
		docmd($a,$aclinter);
		docmd($a,"no ip access-group $aclname in");
		docmd($a,"exit");
	}
	foreach my $line (@acl){
		docmd($a,$line);
	}
	if ($aclon==1){
		docmd($a,$aclinter);
		docmd($a,"ip access-group $aclname in");
		docmd($a,"exit");
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

