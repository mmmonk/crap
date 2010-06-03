#!/bin/sh

if [ -z $2 ]; then
  echo "Usage: $0 inputfile.pcap outputfile.pcap"
else
  tcpdump -n -x -r $1 | perl -e '$i=0;while(<>){if (/^\d/){ $i=0 }; if (/0x0040:  45/) { $i=1;print "\n00000 ";}; if($i==1){s/^.+?:  //;s/(..)(..)\s/$1 $2 /g;print $_;}}' | text2pcap -e 0x800 - $2
fi
