#!/usr/bin/perl

# $Id$

use strict;
use warnings;

my $file=shift;
my $port=2252;

my $l=-1;
my $last="";

open(NGREP,"ngrep -l -I $file -q -t -x tcp and dst port $port and 'tcp[tcpflags] & (tcp-syn|tcp-fin|tcp-rst) == 0' |"); 
while(<NGREP>){
	next if (/^\s*$/);
	if (/^T /){
		$l=0;
		$last=$_;
	}else{
		next if ($l<0);
		$l++;
		chomp;
		s/\s+/:/g;
		s/^://;
		if ($l==1 and /^00:00:00:/){
			$l=-1;
			next;
		}
		if ($l==1){
			print "\n$last";
			(my $o=$_)=~s/^((..:){4}).*/$1/;$o=~s/:$//;
			print "Magic num: $o\n";
			($o=$_)=~s/^(..:){4}((..:){2}).*/$2/;
			$o=hex2dec($o);
			print "Major ver: $o\n";
			($o=$_)=~s/^(..:){6}((..:){2}).*/$2/; 
			$o=hex2dec($o);
			print "Minor ver: $o\n";
			($o=$_)=~s/^(..:){8}((..:){4}).*/$2/;
			$o=hex2dec($o);
			print "Cmd ID   : $o\n";
			if ($o!=1){
				$l=-1;
				next;
			}
			($o=$_)=~s/^(..:){12}((..:){4}).*/$2/;
			$o=hex2dec($o);
			print "Length   : $o\n";

		}
		if ($l==2){
			(my $o=$_)=~s/^((..:){4}).*/$1/;$o=hex2dec($o);
			print "Timestmap: $o\n";
			($o=$_)=~s/^(..:){4}((..:){4}).*/$2/;$o=hex2dec($o);
			print "Msg ID   : $o\n";
			($o=$_)=~s/^(..:){8}((..:){4}).*/$2/;$o=hex2ip($o);
			print "Src IP   : $o\n";
			($o=$_)=~s/^(..:){12}((..:){4}).*/$2/;$o=hex2ip($o);
			print "Dst IP   : $o\n";
		}
		if ($l==3){
			(my $o=$_)=~s/^((..:){2}).*/$1/;$o=hex2dec($o);
			print "Dst port : $o\n";
			print "################\n" unless ($o==80);
			($o=$_)=~s/^(..:){2}((..:){2}).*/$2/;$o=hex2dec($o);
			print "Host off : $o\n";
			($o=$_)=~s/^(..:){4}((..:){2}).*/$2/;$o=hex2dec($o);
			print "Host len : $o\n";
			($o=$_)=~s/^(..:){6}((..:){2}).*/$2/;$o=hex2dec($o);
			print "Prot off : $o\n";
			($o=$_)=~s/^(..:){8}((..:){2}).*/$2/;$o=hex2dec($o);
			print "Prot len : $o\n";
			print "################\n" unless ($o==4);
			($o=$_)=~s/^(..:){10}((..:){2}).*/$2/;$o=hex2dec($o);
			print "URL off  : $o\n";
			($o=$_)=~s/^(..:){12}((..:){2}).*/$2/;$o=hex2dec($o);
			print "URL len  : $o\n";
		}
	}
}
close(NGREP);

sub hex2dec{
	my $out=shift;
	$out=join('',reverse(split(':',$out)));
	$out=hex($out);
	return $out;
}

sub hex2ip{
	my $out=shift;
	my @i=reverse(split(':',$out));
	map { $_=hex($_) } @i;
	return join(".",@i);
} 
