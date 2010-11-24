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

close $sock
