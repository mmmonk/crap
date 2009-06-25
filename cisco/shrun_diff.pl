#!/usr/bin/perl -W

use Net::Telnet::Cisco;
use MIME::Base64;
use Rcs;
use strict;

sub timer;
my $txt = "";
my $ip;
my @out;
my @ips      = ();
my $ipsc     = 0;
my $sendmail = "/usr/lib/sendmail";
my $maindir  = "/home/case/scripts/shrun_diff";

Rcs->quiet(1);
my $rcs = Rcs->new;
$rcs->bindir('/usr/bin');
$rcs->rcsdir("$maindir/arch");
$rcs->workdir("$maindir/current");

open( HOSTS, "/usr/local/netsaint/etc/gen_config/list_blackbox" );
while (<HOSTS>) {
    next unless ($_);
    next if (/^ *\n/);
    $_ = ( split( ";", $_ ) )[0];
    $ip = $_;
    next unless ( $ip =~ /(\d+\.){3}\d+/ );

    @out = ();

#   if ($ip=~m/192\.168\.144\.130/){
#   		@out=get_bsr64k($ip,'am9hdHNBZGdpdA==');
#    		next;
#   }

    if ( $ip =~ m/192\.168\.(112|160|168|176|184|192|200)\.129/ ) {
        @out = get_bsr1k( $ip, 'am9hdHNBZGdpdA==' );
        next;
    }

    @out = get_cisco( $ip, 'case', 'dDNsM3I0bjNrISQ=' );

}
continue {

    my $sizetest = scalar(@out);

    #	print "$ip - $sizetest\n";

    if ( $sizetest > 1 ) {

        $ips[ $ipsc++ ] = $ip;

        my $winchar = chr(13);

        open( FD, "> $maindir/current/$ip.cfg" );
        foreach (@out) {
            next unless ($_);
            s/$winchar//g;
            print FD "$_";
        }
        close(FD);

        $rcs->file("$ip.cfg");
        my $time = timer;
        unless ( open( FD, "$maindir/arch/$ip.cfg,v" ) ) {
            $rcs->ci( '-l', "-m$ip $time", "-t-\".\"" );
            close(FD);
            next;
        }
        if ( $rcs->rcsdiff ) {
            my $tmptxt = "";
            my $triger = 0;
            my $count  = 0;
            foreach my $l ( $rcs->rcsdiff ) {
                unless ( $l =~ m/^[<>\-\n]/ ) {
                    $l = "\n";
                }
                if ( $l =~ /^\n/ ) {
                    $triger = 0;
                    $count  = 0;
                }

                $count++ if ( $triger != 0 );

                next if ( $count == 1 and $l =~ /^---\n/ );
                next if ( ( $l =~ /^---\n/ or $l =~ /^\n/ ) and $tmptxt eq "" );

                $l =~ s/^</rem:/;
                $l =~ s/^>/add:/;
		$l =~ s/(password \d+) .*$/$1 XXXXXXXXXXXXXXX/;

                if ( $l =~
/(cable shared-secret|cable shared-secondary-secret|ntp clock-period|Current configuration)/
                  )
                {
                    $triger = 1;
                    next;
                }
                $tmptxt .= $l;
            }
            unless ( $tmptxt eq "" ) {
                $txt .= "\n<<< $ip - $time >>>\n\n";
                $txt .= $tmptxt;
            }
        }

        $rcs->ci( '-l', "-m$ip $time" );
    }
}
close(HOSTS);

exit if ( $txt eq "" );

my $time = timer;

my $msg = "Cc: <admin\@hell.mm.pl>
To: NOC <noc-priv\@multimedia.pl>
Content-Type: text/plain;
        charset=\"iso-8859-2\"
From: Watcher <confdiff\@multimedia.pl>
Subject: Raport zmian w konfiguracji urzadzen z $time

$txt

";

open( SENDMAIL, "| $sendmail -oi -t " )
  or die "Nie mogê otworzyæ sendmail'a: $!\n";
print SENDMAIL $msg;
close(SENDMAIL) or warn "Sendmail nie zamkn±³ siê ³adnie: $!\n";

sub timer {
    my $sec;
    my $min;
    my $hour;
    my $mday;
    my $mon;
    my $year;
    ( $sec, $min, $hour, $mday, $mon, $year, undef, undef, undef ) =
      localtime(time);
    $year += 1900;
    $mon  += 1;
    $hour = "0$hour" if $hour < 10;
    $mday = "0$mday" if $mday < 10;
    $mon  = "0$mon"  if $mon < 10;
    $min  = "0$min"  if $min < 10;
    $sec  = "0$sec"  if $sec < 10;
    my $ret =
      $year . "-" . $mon . "-" . $mday . "_" . $hour . ":" . $min . ":" . $sec;
    return $ret;
}

sub get_bsr64k {
    # args: <adres ip cmtsa> <haslo>
    my $ip   = shift;
    my $pass = shift;

	$pass = decode_base64($pass);

    my @out;
    eval {
        my $a = Net::Telnet::Cisco->new( Host => $ip, Prompt => '/.+[#>]/' );
        $a->login(
            Password => $pass,
            Prompt   => '/Password/'
        );
        $a->enable($pass);
        return unless ( $a->is_enabled );
        $a->cmd('page off');
        @out = $a->cmd(String=>'show run',Timeout=>900);
        $a->close;
    };
    return if ($@);
    return @out;
}

sub get_bsr1k {
    # args: <adres ip cmtsa> <haslo>
    my $ip   = shift;
    my $pass = shift;

	$pass = decode_base64($pass);

    my @out;
    eval {
        my $a = Net::Telnet::Cisco->new( Host => $ip, Prompt => '/.+[#>]/' );
        $a->login(
            Password => $pass,
            Prompt   => '/Password/',
            Timeout  => 600
        );
        $a->enable($pass);
        return unless ( $a->is_enabled );
        $a->cmd('page off');
        @out = $a->cmd('show run');
    };
    return if ($@);
    return @out;
}

sub get_arris {

    # args: <adres ip cmtsa> <user> <haslo>
    my $ip   = shift;
    my $user = shift;
    my $pass = shift;

	$pass = decode_base64($pass);

    my $a;
    eval {
        $a =
          Net::Telnet->new( Host => $ip, Prompt => '/.+[#>]/', Timeout => 600 );
        unless ( $a->login( $user, $pass ) ) {
            print "ERROR: $!\n kontakt z $ip\n";
            return;
        }
    };
    return if ($@);
    $a->cmd("more off");
    my @out = $a->cmd("putcfg DISPLAY");
    $a->close;
    return @out;
}

sub get_cisco {

    # args: <adres ip cmtsa> <user> <haslo>
    my $ip   = shift;
    my $user = shift;
    my $pass = shift;

    $pass = decode_base64($pass);

    my @out;
    eval {
        my $a = Net::Telnet::Cisco->new( Host => $ip, Timeout => 600 );
        unless ( $a->login( $user, $pass ) ) {
            print "ERROR: $!\n kontakt z $ip\n";
            return;
        }
        $a->cmd('term len 0');
        @out = $a->cmd('sh run');
        $a->close;
    };
    return if ($@);
    return @out;
}

