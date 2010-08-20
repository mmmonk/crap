#!/usr/bin/perl -wW

# $Id$





use strict;
use integer;

use LWP::UserAgent;

my $postmaster = '/home/postmaster/Maildir/new';
my $sendmail   = '/usr/lib/sendmail';
my $rundir     = '/home/dsbl_cleaner';

my $timestamp = 0;
my $webtext   = '';

my $mailhead = "From: dsbl-org-remover\@banana.republic
To: abuse\@microsoft.com
Subject: [DSBL] - dsbl.org remove confirmation 

----------------------------------------------------------
";

if ( -f "$rundir/dsbl-org.dat" ) {
    open( FD, "$rundir/dsbl-org.dat" );
    $timestamp = <FD>;
    close(FD);
}

opendir( DIR, $postmaster );
while ( my $file = readdir(DIR) ) {
    next if ( $file =~ /^\./ );

    ( my $test = $file ) =~ s/(^\d+)\.\d+\..*/$1/;

    if ( $test > $timestamp ) {
        $timestamp = $test;

        my $dsbl = 0;
        open( FD, "$postmaster/$file" );
        while (<FD>) {
            next unless (/dsbl\.org\/removal_confirm/);
            $dsbl = 1;
            chomp;
            my $ua = LWP::UserAgent->new;
            $ua->agent(
"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; .NET CLR 1.1.4322"
            );
            my $req = HTTP::Request->new( GET => "$_" );
            my $res = $ua->request($req);
            if ( $res->is_success ) {
                $webtext = join( " ", $res->content );
                $dsbl = 2;
            }
        }
        if ( $dsbl > 0 ) {
            seek( FD, 0, 0 );
            my @txt = <FD>;

            open( SENDMAIL, "| $sendmail -oi -t " )
              or die "Nie mogê otworzyæ sendmail'a: $!\n";
            print SENDMAIL $mailhead;
            if ( $dsbl == 2 ) {
                print SENDMAIL $webtext;
            }
            print SENDMAIL @txt;
            close(SENDMAIL) or warn "Sendmail nie zamkn±³ siê ³adnie: $!\n";
        }
        close(FD);
    }
}
closedir(DIR);

open( FD, "> $rundir/dsbl-org.dat" );
print FD "$timestamp";
close(FD);
