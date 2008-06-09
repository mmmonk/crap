#!/usr/bin/perl

use strict;
use XML::RSS;
use LWP::UserAgent;

my $ua = LWP::UserAgent->new;
$ua->env_proxy;

system('find /home/torsec/torrents/watch -type f -ctime +3 -name "*.torrent" -exec rm -f {} \;');

my @unwanted = (
'Architectural Record',
'ArtzMania',
'BusinessWeek',
'BusinessWeek',
'Computer Power User',
'Computer Shopper',
'Electronic Gaming Monthly',
'IEEE',
'Macworld',
'Maximum PC Magazine',
'National Geographic',
'Nature',
'PC Magazine',
'PC World',
'Personal Computer World',
'Photoshop Creative',
'Popular Science',
'Science',
'Scientific American',
'Smart Computing',
'Smartphone and Pocket PC',
'The Economist',
'US News And World Report'
);

my $req = HTTP::Request->new(GET => "http://www.ebookshare.net/plus/rss/index.xml");
my $res = $ua->request($req);

if ($res->is_success) {
	my $rss = new XML::RSS;	
	$rss->parse($res->content);
	foreach my $item (@{$rss->{'items'}}) {
		my $tw = $item->{'title'};
		my $check = 0;
		foreach my $test_title (@unwanted){
			$check = 1 if ($tw=~/^$test_title/i);
		}
		next if ($check == 1);
		$tw = HTTP::Request->new(GET => $item->{'link'});
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
