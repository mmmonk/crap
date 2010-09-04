#!/usr/bin/perl

# $Id$

use strict;
use integer;
use warnings;

$|=1;

use Expect;
use POSIX qw(:termios_h);

my $hostfile="cmd.hosts";
my $hostcmd="cmd.txt";

my %auth=();
$auth{"user"} = ['xxxxxx'];

my @users = ("user"); 

my @hosts;
if ( -f $hostfile ){
	open(FD,$hostfile);
	while(<FD>){
		chomp;
		push(@hosts,$_);
	}
	close(FD);
}

my @preloadcmd=();
open(FD,$hostcmd) or die "$!\n";
while(<FD>){
	chomp;
	push(@preloadcmd,$_);
}
close(FD);


my $logfile="sessions/session_".(timer()).".txt";

my $end=0;

foreach my $host (@hosts){

	next unless ($host);

	$end=0;

	my $exp = Expect->new();

	print "---- $host ----\n";

	foreach my $user (@users){ 

		next if ($end==1);

		print "\n";
#		$exp = Expect->spawn("ssh -t 192.168.10.10 'ssh -t -l $user $host' 2>&1");
		$exp = Expect->spawn("ssh -t -l $user $host 2>&1");

		$exp->expect(10,[qr/you sure you want to continue connecting/ => sub { my $e=shift;$e->send("yes\n");}],
				[qr/RSA modulus too small: \d+ < minimum 768 bits/ => sub {$end=2;}],
				[qr/(Permission denied|.+assword:)/i => sub {$end=4;}]);

		my $passa=$auth{$user};
		foreach my $pass (@$passa){

			next if ($end==1);

			unless ($exp->pid()){
				print "\n";
				$exp = Expect->spawn("ssh -t 192.168.10.10 'ssh -t -l $user $host' 2>&1");
			}
			if ($end==4){
				$exp->send("$pass\n");
			}
			$exp->expect(10,[qr/.+assword:/ => sub { my $e=shift;$e->send("$pass\n");}],
					[qr/^(.*?)#/ => sub { my $e=shift;$e->send("\n");$end=1;}]);
			unless ($end==1){
				$exp->expect(10,[qr/^(.*?)#/ => sub { $end=1;} ],
					[qr/.+assword:/i => sub {$end=4;}],
					[qr/Connection to 192.168.10.10 closed./ => sub {$end=3}]);
			}
		}
	}

	if ($end==1){

			$exp->send("term len 0\n");
			
			$exp->log_file($logfile);
			$exp->print_log_file("\n---- $host ---- ".(timer())." ----\n");

			sleep 1;
			foreach my $cmd (@preloadcmd){
				$_=$cmd;
#					print "$_\n";
				$exp->expect(60,[qr/^(.*?)(#|\? |\? \[.+?\])$/ => sub { my $e=shift;$e->send("$_\n");}]);
			}
			$exp->expect(10,[qr/^(.*?)#/]);

			$exp->send("exit\n");
			$exp->expect(10,[qr/^(.*?)#/]);
			$exp->log_file(undef);
	}

	$exp->hard_close();
	print "\n";
}


sub cwait{
	select(undef, undef, undef, 0.5);
#	sleep 1;
}

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
