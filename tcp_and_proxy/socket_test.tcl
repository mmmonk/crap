#!/usr/bin/tclsh

#
# $Id$
#

set socketimeout 500 ;# in ms

if { $argc != 2 } {
  puts "usage: $argv0 host port"
  exit
}
set host [lindex $argv 0]
set port [lindex $argv 1]

# procedure to be used in fileevent
proc stok {sock} {
  global state
  
  # we could get here because of the error
  set resp [fconfigure $sock -error]

  if {$resp == "" } { 
    set state ok
  } else {
    set state closed 
  }
}

# set the timeout value
after $socketimeout set state timeout 

# do non-blocking connect
set sock [socket -async $host $port ] 

# wait for the socket to be writetable
fileevent $sock writable { stok $sock }

# otherwise timeout here
vwait state

after cancel set state timeout 

puts $state

if { $state == "ok" } {

  fconfigure $sock -blocking on

  set client_hello "160300005d0100005903003d7d24fa8873270c0104687df7dc99547a04b314d277301874824318eb445ff2201b483eeaf33bfc4207e4ee6d9a97194cfac3bf363baa5f6ab6e8b545e684f4df00120004feff000afefe000900640062000300060100"

  set hello_length  [ string length $client_hello ]
  puts -nonewline $sock [ binary format "H${hello_length}" $client_hello ]
  flush $sock
  
  set lines [ read $sock 100 ]

  if { ![ binary scan $lines "@0H6" res ] } {

    puts "ssl failed"

  } else {

    puts $res 

  }
}

close $sock
