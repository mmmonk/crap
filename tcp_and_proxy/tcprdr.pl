#!/usr/bin/perl

# $Id$





#use warnings;
use strict;
use Socket;
use POSIX qw(setuid setgid setsid);

die "Only r00t can run this script\n" if ($> != 0);

sub logwr;

my $uid=getpwnam('nobody');
my $gid=getgrnam('nobody');

logwr("changing dir to /");
chdir("/");

#my $chroot="/var/tmp";
#logwr("chroot to $chroot");
#chroot $chroot or die "$!";

my $sin = sockaddr_in (443,&INADDR_ANY);
socket(sock,&AF_INET,&SOCK_STREAM,getprotobyname('tcp')) or die "socket: $!";
bind(sock,$sin) or die "bind: $!";
listen(sock,5) or die "listen: $!";

logwr("droping privilges to user=nobody, uid=$uid, group=nobody, gid=$gid");
setgid($gid) or die "Can't setgid: $!";
setuid($uid) or die "Can't setuid: $!";

logwr("redirecting STDIN and STDOUT to /dev/null");
open STDIN, '/dev/null' or die "Can't read /dev/null: $!";
open STDOUT, '>/dev/null' or die "Can't write to /dev/null: $!";

logwr("becoming a deamon");
defined(my $pid = fork) or die "Can't fork: $!";
if ($pid){
	logwr("PID:$pid");
	exit;
}
setsid;

while ( 1 ){
	my $addr;
	($addr = accept(peer,sock)) or die "accept: $!";

	if ( fork ){
		next;
	}else{
		my $dat;
		my $datnr=sysread peer, $dat, 500;

		my @rdrp;
		if ( $dat =~/^testssh/ ){
			@rdrp=("127.0.0.1","22");
		}else{
			@rdrp=("127.0.0.1","80");
		}

		my ($peerport,$peeraddr)=sockaddr_in($addr);

		my $sin = sockaddr_in ($rdrp[1],inet_aton($rdrp[0]));
		socket(rdr,&AF_INET,&SOCK_STREAM,getprotobyname('tcp')) or die "socket: $!";
		connect(rdr,$sin) or die "connect: $!";

		unless ($rdrp[0] eq "127.0.0.1" and $rdrp[1] eq "22"){
			syswrite rdr,$dat,$datnr;
		}

		logwr("O ".inet_ntoa($peeraddr).":".$peerport." > ".$rdrp[0].":".$rdrp[1]);

		if ( my $pid = fork ) {
			my $data;
			while ( 1 ) {
				my $bl = sysread peer, $data, 1300;
				if ( not $bl ) {
					shutdown(rdr,&SHUT_RDWR);
					shutdown(peer,&SHUT_RDWR);
					exit 0;
				}
				syswrite rdr, $data, $bl;
			}
		}else{
			my $data;
			while ( 1 ) {
				my $bl = sysread rdr, $data, 1300;
				if ( not $bl ) {
					logwr("C ".inet_ntoa($peeraddr).":".$peerport." > ".$rdrp[0].":".$rdrp[1]);
					exit 0;
				}
				syswrite peer, $data, $bl;
			}
		}
		exit 0;
	}
}
shutdown(sock,&SHUT_RDWR);

sub timer{
        my ($sec,$min,$hour,$mday,$mon);
	my @abbr = qw( Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec );
        ($sec,$min,$hour,$mday,$mon,undef,undef,undef,undef) = localtime(time);
        $mon=$abbr[$mon];
	$sec="0$sec" if ($sec < 10);
	$min="0$min" if ($min < 10);
	$hour="0$hour" if ($hour < 10);
        $mday=" $mday" if $mday < 10;
        my $ret="$mon $mday $hour:$min:$sec";
        return $ret;
}

sub logwr{
	my $ts=timer();
	my $msg=shift;
	warn "$ts tcprdr: $msg\n";
}
