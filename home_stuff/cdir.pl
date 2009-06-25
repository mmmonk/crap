#!/usr/bin/perl -W

#use strict;

use Digest::MD5;

sub ReNameFile;

my $recurs=0;
my $opt=shift;
my $i=0;

$opt="nr" if (!defined($opt));
$recurs=1 if ($opt eq "r");

my %hash=();
my %name=();

ReNameFile(".");

sub ReNameFile{
	my $dir=shift;
	$i++;
	my $od="dir$i";
	print "CWD: $dir\n";
	if (opendir($od,"$dir")){
		while(my $file=readdir($od)){
        		if (defined($file) && $file ne ".." && $file ne "."){
				
				my $mode=(stat("$dir/$file"))[2];
				($mode)=split(//,$mode);
				if ($mode == 1){
#					print "DIR: $dir/$file\n";
					ReNameFile("$dir/$file") if ($recurs == 1);
				}
				my $new=lc($file);
				$new=~tr/±êæ¶ñó³¿¼/aecsnolzz/;
				$new=~tr/¡ÊÆ¦ÑÓ£¯¬/aecsnolzz/;
				$new=~s/( |,|\[|\]|\(|\)|'|:|;|!|-|\.|`)/_/g;
				$new=~s/&/_and_/g;
				$new=~s/_+/_/g;
				$new=~s/(^_|_$)//g;
				unless ($mode==1){
					$new=~s/(.*)_(.+)$/$1.$2/g;
				}

#				my $md5c= Digest::MD5->new;
#				$md5c->addfile($file);
#				my $md5= $md5c->hexdigest;
#
#				if (exists($hash{$md5})){
#					print "$file is equal $hash{$md5}\n";
#				}else{
#					$hash{$md5}="$file";
#				}


				if ($new ne $file){
                        		if (open(TEST,$new)){
                                		print "DIDN'T RENAME: $file\n";
                        		}else{
						print "$dir/$file\n";
#						print "$dir/$new\n";
						rename("$dir/$file","$dir/$new") or print "ERROR: $file\n";
                        		}
	                       		close(TEST);
				}
        		}
		}
	}
	close($od);
}
