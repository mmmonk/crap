#!/usr/bin/perl -w

use strict;
use integer;

my @last=("You cannot achieve the impossible without attempting the absurd.",
	  " There's nothing very mysterious about you, except that nobody\n". 
          "      really knows your origin, purpose, or destination.        ",
	  "           Portable, adj.: Survives system reboot.              ",
	  "         Assumption is the mother of all screw-ups.             ",
	  "     Signals don't kill programs.  Programs kill programs.      ",
	  "  Thinking you know something is a sure way to blind yourself.  ",
          "             Neckties strangle clear thinking.                  ",
	  "        Science is true.  Don't be misled by facts.             ",
	  "            Never be afraid to try something new.             \n".
          "Remember, amateurs built the ark. Professionals built the Titanic"
);


srand(time);
srand(int(rand(time)));

print "Marek £ukaszuk\nNetwork Analyst @ GE Money Bank Poland - Phone +48 58 308 50 55\n";
my $won=int(rand($#last+1)); # +3 dla dwóch poni¿szych randomów ;)
if ($won<=$#last){
	print $last[$won];
}else{
	if ($won==$#last+1){
		for (my $i=0;$i<64;$i++){
			print int(rand(2));
		}
	}else{
		print "0x";
		for (my $i=0;$i<62;$i++){
			printf("%x",(int(rand(16))));
		}
	}
}
print "\n";

