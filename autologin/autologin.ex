#!/usr/local/bin/expect --

;# $Id$

package require base64

set var1 "base64encodedpass1"
set var2 "base64encodedpass2"
set var3 "base64encodedpass3"
set var4 "base64encodedpass4"
set ver1 "base64encodeden1"
set ver2 "base64encodeden2"
set ver3 "base64encodeden3"

;#set send_slow  {2  .001}
set send_slow {10 .01}
set timeout 60

if {![regexp ".+/(.+$)" $argv0 "" host]} {
	exit
}

if {[regexp "^ubr7200-" $host ]} {
        set pass [::base64::decode $var2]
        set enab [::base64::decode $ver3]
        set user "user2"
        set cmd "/usr/bin/ssh -t $user@$host"

} elseif { [regexp "-sw0" $host ]} {
	set pass [::base64::decode $var2]
	set enab [::base64::decode $ver2] 
	set user "admin"
	set cmd "/usr/bin/telnet $host"

} elseif { [regexp "(^eb|^tyskie)" $host]} {
	set pass [::base64::decode $var4]
	set enab [::base64::decode $ver3]
	set user "god"
	set cmd "/usr/bin/telnet $host"

} else {
	set pass [::base64::decode $var1]
	set enab [::base64::decode $ver3]
	set user "user"
	set cmd "/usr/bin/ssh -t $user@$host"
}

;# from this moment whole login process is hidden
log_user 0

;# we are connecting to the remote host, throught another ssh connection
spawn /usr/bin/ssh -2 -4 -C -c blowfish-cbc -t CERBER_HOST "$cmd" 

expect timeout {
	send_user "failed to connect - timeout\n"
	exit
} eof {
	send_user "failed to connect\n"
	exit
} "Are you sure you want to continue connecting (yes/no)?" {
	send_user "!!! host $host key has changed !!!\n"
	send -s "yes\r"
	sleep 1
	exit
} "Enter passphrase for key*" {
	send_user "Please run ssh-add first\n"
	exit
} "sername:*" { 
	send -s "$user\r" 
	expect "assword:*" { 
		send -s "$pass\n"
	} 
} "assword:*" { 
	send -s "$pass\r" 
}

expect "*>*" { 
	send -s "en\r" 
	expect "Password:*" { 
		send -s "$enab\r"
	}
	expect "*#*" {
		send -s "term mon\r"
	}
} "*#*" { 
	send -s "term mon\r"
}

expect "*#*" { send -s "\r" }

log_user 1
set time     [ timestamp -format "%Y/%m/%d %H:%M:%S"]
set filetime [ timestamp -format "%Y%m%d_%H%M%S"]

send_user "\nLogin time is $time\n"

log_file "/usr/home/case/store/work/_archives_worklogs/$host-$filetime.log"

send_log "\n---------- log start at $time ----------\n"

;# we will use the CTRL-A key sequence to send commands to expect
;# set KEY \001 

interact {
	;# so that we don't get logout when idle
	timeout 180 { send " \b"}

	;# aliases
	-echo \001sr\r 	{ 
		send "\nsh run\r"
	}	
	-echo \001ud\r 	{ 
		send "\nshow debug\rundebug all\r"
	}
	-echo \001sid 	{ 
		interact -echo -re "(.*)\r" return
		send "\nsh interf descr $interact_out(1,string)\r" 
	}
	-echo \001siib {
		interact -echo -re "(.*)\r" return
		send "\nsh ip interf brief $interact_out(1,string)\r"
	}
	-echo \001ct {
		interact -echo -re "(.*)\r" return
#		if {[string length $interact_out(1,string) > 0]} {
			send "\nsh crypto isakmp sa | i $interact_out(1,string)_.*QM_IDLE.*ACTIVE\r"
			expect "sh crypto isakmp sa | i $interact_out(1,string)_.*QM_IDLE.*ACTIVE\r"
			expect -re "(.*)#.*"
			regsub -all "(\n|\r| )+" $expect_out(buffer) "_" line 
#			regsub -all " +" $line "_" line
			if {[regexp ".+_QM_IDLE_(.+)_.+_ACTIVE_.*$" $line "" isakmp_sa]} {
				send "clear crypto isakmp $isakmp_sa\n"
				expect "*#*"
				send "clear crypto sa peer $interact_out(1,string)\r"
			}
#		}
	}
}

set time     [ timestamp -format "%Y/%m/%d %H:%M:%S"]
send_log "\n---------- log close at $time ----------\n"
log_file
exec /usr/bin/bzip2 /home/user/_archives_worklogs/$host-$filetime.log
exit
