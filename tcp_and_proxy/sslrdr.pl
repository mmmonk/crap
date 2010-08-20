#!/usr/bin/perl

# $Id$





my $basedir="/usr/home/case/store/priv/rdr/";
my $logfile=$basedir."sslrdr.log";

#use warnings;
use strict;
use Socket;
use POSIX qw(setuid setgid setsid);
use Net::SSLeay qw(die_now die_if_ssl_error);

die "Only r00t can run this script\n" if ($> != 0);
die "$basedir doesn't exists\n" if ( ! -d $basedir);

sub make_cert;
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

Net::SSLeay::SSLeay_add_ssl_algorithms();
Net::SSLeay::randomize();

my $cert_pem=$basedir."cert.pem";
my $key_pem=$basedir."key.pem";

if ( ! -f $cert_pem or ! -f $key_pem ){
	logwr("genereting cert files");
	make_cert;
}

my $ctx = Net::SSLeay::CTX_v23_new() or die ("Failed to create SSL_CTX $!");
my $cipher_list='DH-RSA-AES256-SHA:AES256-SHA:AES';
Net::SSLeay::CTX_set_cipher_list($ctx,$cipher_list);
Net::SSLeay::set_server_cert_and_key($ctx, $cert_pem, $key_pem) or die "key: $!";

logwr("droping privilges to user=nobody, uid=$uid, group=nobody, gid=$gid");
setgid($gid) or die "Can't setgid: $!";
setuid($uid) or die "Can't setuid: $!";

logwr("redirecting STDIN and STDOUT to /dev/null");
open STDIN, '/dev/null' or die "Can't read /dev/null: $!";
open STDOUT, '>/dev/null' or die "Can't write to /dev/null: $!";

logwr("becoming a deamon");
defined(my $pid = fork) or die "Can't fork: $!";
if ($pid){
	exit;
}
setsid;

logwr("PID: $$");

while ( 1 ){
	my $addr;
	($addr = accept(peer,sock)) or die "accept: $!";

	if ( fork ){
		next;
	}else{
		my $ssl = Net::SSLeay::new($ctx) or die ("Failed to create SSL $!");
		Net::SSLeay::set_fd($ssl, fileno(peer));
		Net::SSLeay::accept($ssl) or die "$!";
		die_if_ssl_error("ssl accept($!):");

		my $dat=Net::SSLeay::read($ssl);;

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
			syswrite rdr,$dat,length($dat);
		}

		logwr("O ".inet_ntoa($peeraddr).":".$peerport." > ".$rdrp[0].":".$rdrp[1]." cipher:".Net::SSLeay::get_cipher($ssl));

		if ( my $pid = fork ) {
			my $data;
			while ( 1 ) {
				$data = Net::SSLeay::read($ssl);
				if ( ! $data ) {
					shutdown(rdr,&SHUT_RDWR);
					shutdown(peer,&SHUT_RDWR);
					exit 0;
				}
				syswrite rdr, $data, length($data);
			}
		}else{
			my $data;
			while ( 1 ) {
				my $bl = sysread rdr, $data, 1300;
				if ( not $bl ) {
					logwr("C ".inet_ntoa($peeraddr).":".$peerport." > ".$rdrp[0].":".$rdrp[1]);
					exit 0;
				}
				Net::SSLeay::write($ssl, $data);
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
	warn "$ts sslrdr: $msg\n";
}


sub make_cert{

	my $sslbin = '/usr/bin/openssl';

	die "Can't open $sslbin: $!" unless ( -f $sslbin );

	my $reqconf=$basedir."req.conf";
	if (! -f $reqconf){
		open(REQ,"> $reqconf");
		print REQ "[ req ]
default_bits            = 1024
default_keyfile         = privkey.pem
distinguished_name      = req_distinguished_name
attributes              = req_attr
encrypt_rsa_key         = no
 
[ req_distinguished_name ]
countryName             = Country Name (2 letter code)
countryName_min         = 2
countryName_max         = 2
countryName_default     = PL
 
stateOrProvinceName     = State or Province Name (optional)
 
localityName            = Locality Name (eg, city)
localityName_default    = Dupa 
 
organizationName        = Organization Name (eg, company)
 
organizationalUnitName  = Organizational Unit Name (eg, section)
 
commonName              = Common Name (the name of your machine)
commonName_max          = 64
 
emailAddress            = Email Address
emailAddress_max        = 40
 
# Challenge password is used for delievering the cert (or what)???
 
[ req_attr ]
challengePassword       = A challenge password
challengePassword_min   = 0
challengePassword_max   = 80
 
#EOF";
		close(REQ);
	}
	
	open (REQ, "|$sslbin req -config $basedir/req.conf -x509 -days 365 -new -keyout $basedir/key.pem > $basedir/cert.pem 2> /dev/null") or die "cant open req. check your path ($!)";
	print REQ "XX\nDUPA\ndupa dupa\ndupa Dupa\nDupa Organization\nTest Unit\n127.0.0.1\ndupa\@localhost.localdomain\n";
	close REQ;
	system "$sslbin verify $basedir/cert.pem > /dev/null 2> /dev/null"; 
	system "$sslbin rsa -in $basedir/key.pem -des -passout pass:secret -out $basedir/key.pem.e > /dev/null 2> /dev/null"; 

	my $hash = `$sslbin x509 -inform pem -hash -noout <$basedir/cert.pem > /dev/null 2>&1`;
	chomp $hash;
	unlink "$basedir/$hash.0";
	unlink "$basedir/key.pem.e";
	unlink "$basedir/req.conf";
}
