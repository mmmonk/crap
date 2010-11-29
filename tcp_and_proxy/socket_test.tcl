#!/usr/bin/tclsh

#
# $Id$
#

if { $argc != 2 } {
  puts "usage: $argv0 host port"
  exit
}

set host [lindex $argv 0]
set port [lindex $argv 1]

set sockettimeout 500 ;# in ms
# to get value bellow do: openssl s_client -debug -msg -ssl3 -connect google.com:443 | head -n 20
set sslclient_hello "16030000540100005003004cf0a8b1885a4d8dd81347e1a3dfc98a7e4bdb126a44b5b969f10c219627a4e800002800390038003500160013000a00330032002f000500040015001200090014001100080006000300ff02010"
set sslhello_length  [ string length $sslclient_hello ]

########################
# procedure to be used in fileevent to test TCP
#
proc stok {sock} {
  
  # we could get here because of an error
  set resp [fconfigure $sock -error]

  if {$resp == "" } { 
    return "tcp:ok" 
  }
 
  return "tcp:closed" 
}

########################
# procedure to be used in fileevent to test SSL
#
proc sslok {sock} {

  set lines [ read $sock 100 ]

  if { ![ binary scan $lines "@0H6" resp ] } {
    return "tcp:ok, ssl:binary scan error"
  }
  
  if { $resp == "150300" } {
    return "ok"
  } 

  return "tcp:ok, ssl:bad response"
}

########################
### main
########################

# set the timeout value
after $sockettimeout set tcpstate "tcp:timeout" 

# create a non-blocking socket 
set sock [socket -async $host $port ] 

# read needs this explicitly defined, strange
fconfigure $sock -blocking no

# wait for the socket to be writable
fileevent $sock writable { set tcpstate [stok $sock ] } 

# otherwise timeout here
vwait tcpstate

after cancel set tcpstate "tcp:timeout" 

set state $tcpstate

if { $tcpstate == "tcp:ok" } {

  # we send predefine ssl client hello here - simple, but it works
  puts -nonewline $sock [ binary format "H${sslhello_length}" $sslclient_hello ]
  flush $sock

  after $sockettimeout set sslstate "tcp:ok, ssl:timeout" 
  
  fileevent $sock readable { set sslstate [sslok $sock ] }

  vwait sslstate

  after cancel set sslstate "tcp:ok, ssl:timeout" 

  set state $sslstate
}

puts $state

close $sock
