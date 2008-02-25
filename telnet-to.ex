#!/usr/bin/expect --

;# Author: Marek Lukaszuk <m.lukaszuk<at>gmail.com>
;# Copyright (c) 2005, Marek £ukaszuk 
;# BSD License at http://monkey.geeks.pl/bsd/

package require base64

set pass1 "base64_encoded_password1"
set pass2 "base64_encoded_password2"
set pass3 "base64_encoded_password3"
set enabl1 "base64_encoded_password4"


set send_slow  {2  .001}
set timeout 60

if {![regexp ".+/(.+$)" $argv0 "" host]} {
	exit
}

send_user "$host\n"

log_user 0 
spawn telnet $host

# Motorola BSR 
if {[string match $host "192.168.12.2"] ||
    [string match $host "192.168.14.3"] ||
    [string match $host "192.168.10.2"] || 
    [string match $host "192.168.18.2"] || 
    [string match $host "192.168.16.2"] ||
    [string match $host "192.168.14.2"] || 
    [string match $host "192.168.12.2"] || 
    [string match $host "192.168.20.2"]
    } {
	
	set pass [::base64::decode $pass2]
	expect -re "Password:.*" 	{ send -s "$pass\r" }
	expect -re ".*>" 		{ send -s "en\r" }
	expect -re "Password:.*" 	{ send -s "$pass\r" }

# Arris
} elseif { [string match $host "1.3.0.1"] } {
	set pass [::base64::decode $pass2]
	expect -re "Login:*" 		{ send -s "root\r" }
	expect -re "Password:.*" 	{ send -s "$pass\r" }

# some router with enable secret 
} elseif { [string match $host "1.12.2.0"] } {
	set pass [::base64::decode $pass1]
	set enab [::base64::decode $enabl1]
	expect -re "Username:.*"	{ send -s "case\r" }
	expect -re "Password:.*"	{ send -s "$pass\r" }
	expect "*>*"			{ send -s "en\r" }
	expect -re "Password:.*"	{ send -s "$enab\r"}
	expect "*#*"			{ send -s "term mon\r" }

# default
} else {
	set pass [::base64::decode $pass1]
	expect -re "Username:.*" 	{ send -s "case\r" }
	expect -re "Password:.*" 	{ send -s "$pass\r" }
	expect "*#*"			{ send -s "term mon\r" }
	expect -re "(.*#|.*>)"		{ send -s "\r" }	
}

log_user 1
set time     [ timestamp -format "%Y/%m/%d %H:%M:%S"]
set filetime [ timestamp -format "%Y%m%d_%H%M%S"]
send_user "\nLogin time is $time\n"
log_file "/home/user/telnet_arch/$host-$filetime.log"
send_log "\n---------- log start at $time ----------\n"
interact
send_log "\n---------- log close at $time ----------\n"

exit
