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

  # to get value bellow do: openssl s_client -debug -msg -ssl3 -connect google.com:443 | head -n 20
  
  set client_hello "16030000540100005003004cf033aeb88cf0efec4a0b0f68eaaa666f2b65d06654dfdcd1ad9bd3bd1b507f00002800390038003500160013000a00330032002f000500040015001200090014001100080006000300ff0201"

  set hello_length  [ string length $client_hello ]
  puts -nonewline $sock [ binary format "H${hello_length}" $client_hello ]
  flush $sock
  
  set lines [ read $sock 100 ]

  if { ![ binary scan $lines "@0H6" res ] } {

    puts "ssl failed"

  } else { 
    if { $res == "150300" } {
    
      puts "got correct ssl server handshake"

    } else {

      puts "I don't understand the answer from the server"

    }
  }
}

close $sock
