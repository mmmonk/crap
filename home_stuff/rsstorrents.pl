#!/usr/bin/perl

# $Id$

use strict;
use XML::RSS;
use LWP::UserAgent;

my $ua = LWP::UserAgent->new;
$ua->env_proxy;

my $req = HTTP::Request->new(GET => "http://www.ebookshare.net/plus/rss/index.xml");
my $res = $ua->request($req);

if ($res->is_success) {
        my $rss = new XML::RSS;
        $rss->parse($res->content);
        foreach my $item (@{$rss->{'items'}}) {
                my $tw = HTTP::Request->new(GET => $item->{'link'});
                my $tr = $ua->request($tw);
                if ($tr->is_success) {
                        my $tf=$tr->content;
                        $tf=~s/^.*(\/download\.php\?id=\d+).*/$1/s;
                        $tf="http://www.ebookshare.net$tf";
                        my $filename=$tf;
                        $filename=~s/^.*id=(\d+).*/$1.torrent/;
                        $filename="/home/torsec/torrents/watch/".$filename;
                        if ( ! -f $filename){
                                my $filereq = HTTP::Request->new(GET => $tf );
                                my $fileres = $ua->request($filereq);
                                if ($fileres->is_success){
                                        open(TOR,"> $filename");
                                        print TOR $fileres->content;
                                        close(TOR);
                                }
                        }
                }
        }
} else {
        print $res->status_line, "\n";
}

