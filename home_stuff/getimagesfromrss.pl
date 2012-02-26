#!/usr/bin/perl

use strict;
use warnings;


use XML::FeedPP;
use LWP::UserAgent;


my $ua = LWP::UserAgent->new;
$ua->agent("ImageDownloader/0.9 ");

my $source = 'http://feeds.feedburner.com/LivesciencecomAmazingImages';
my $feed = XML::FeedPP->new( $source );
foreach my $item ( $feed->get_item() ) {
	print $item->link(),"\n";
	my $req = HTTP::Request->new(GET => $item->link());
	my $res = $ua->request($req);
	next unless ($res->is_success);
	print $res->content;
}

