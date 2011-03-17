#!/usr/bin/perl

# $Id$

use warnings;
use integer;
use strict;

my @ans=("As I see it, yes",
"It is certain",
"It is decidedly so",
"Most likely",
"Outlook good",
"Signs point to yes",
"Without a doubt",
"Yes",
"Yes - definitely",
"You may rely on it",
"Reply hazy, try again",
"Ask again later",
"Better not tell you now",
"Cannot predict now",
"Concentrate and ask again",
"Don't count on it",
"My reply is no",
"My sources say no",
"Outlook not so good",
"Very doubtful");

my %params=map{my($name,$value)=split/\=/;$name => $value} map{split /\&/} $ENV{"QUERY_STRING"};

print "Content-type: text/html\n\n
<html><head><title>Advanced NSM troubleshooting tool</title>
<style type=\"text/css\">
<!--
form {
text-align:center; border: 1px 
}
-->
</style>
</head><body>
<h1 align=\"center\"><a href=\"?\">Advanced NSM troubleshooting tool</a><br/>training is required to use it</a></h1><p align=\"center\">
Please think of a question that can be answered with either <b>yes</b> or <b>no</b> and then press the button,<br/> you question will be pondered by an expert and you shall receive an answer shortly:<br/>
<form  method=\"get\" enctype=\"text/plain\"><input type=\"hidden\" name=\"ans\" value=\"1\"/>\n";

if (exists($params{"ans"})){
  sleep 1;
  srand(time());
  my $i=int(rand($#ans));
  print "<input type=\"submit\" value=\"GIVE ME ANOTHER ANSWER\"/></form><br/></p><p align=\"center\">THE ANSWER IS: <u><b>".$ans[$i]."</b></u>";
}else{
  print "<input type=\"submit\" value=\"GIVE ME THE ANSWER\"/></form>";
}

print "</p></body></html>\n";
