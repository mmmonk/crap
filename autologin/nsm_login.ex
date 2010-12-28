#!/usr/bin/expect -f

;# $Id$

set send_slow {10 .01}
set timeout 60

if { $argc == 0 } {
  puts "
Usage: $argv0 <username@>host <password>

If not specified username defaults to \"root\" and password to \"netscreen\".

The connection to target host is done with normal ssh command without any arguments. 
My suggestion is to use ~/.ssh/config for any non standard options.
" 
  exit
} else {
  set host [lindex $argv 0]
  set user "root"
  set pass "netscreen"
  if { [regexp @ $host] } {
    regexp {(\S+?)@} $host match user
    regexp {@(\S+)} $host match host
  }
  if { $argc > 1 } {
    set pass [lindex $argv 1]
  }
}

spawn ssh -o "ControlPersist no" $user@$host

set time     [ timestamp -format "%Y/%m/%d %H:%M:%S"]
set filetime [ timestamp -format "%Y%m%d_%H%M%S"]

puts "\033]0;$host $filetime\007"

expect timeout {
  send_user "connection timeout\n"
  exit
} eof {
  send_user "got eof\n"
  exit
} "Permission denied, please try again." {
  send_user "wrong credentials\n"
  exit
} "Are you sure you want to continue connecting (yes/no)?" {
  send -s "yes\r"
  exp_continue
} "assword:" {
  send -s "$pass\r"
  exp_continue
} "Run NSMXPress system setup" {
  send -s "n"
  exp_continue
} "*$ " {
  send -s "sudo su -\r"
  exp_continue
} "*# " {
  send -s "unset TMOUT\r"
}

expect "*#" {
  send "ifconfig | perl -nle'/dr:(172.30.\\S+)/&&print\$1'\r"
}

expect "*#" {
  set ourip [regexp -inline -- {172\.30\.\d+\.\d+} $expect_out(buffer)]
  send "\r"
}

expect "*# " {
  log_file "/home/case/store/work/_archives_worklogs/$host-$filetime.log"
  send_log "\n---------- log start at $time ----------\n"

  send_user "
--- Key shortcuts ---
Ctrl+A l - types \"netscreen\\r\"
Ctrl+A p - types \"rpm -qa | grep netscreen | xargs -r rpm -e ; rm -rf /var/netscreen/*/* /usr/netscreen/*\" <- noticed no \\r
Ctrl+A i - can be entered during the nsm installtion will answer all the questions (clean install Gui+Dev if installing from scratch or just refresh otherwise)
Ctrl+A u - correct the customer db (super password, IPs)

Have fun :)\n"

  send "\r"

  interact {

    \001l { send "$pass\r" }

    \001p { send "rpm -qa | grep netscreen | xargs -r rpm -e ; rm -rf /var/netscreen/*/* /usr/netscreen/*" }

    \001i { 
        send  "\r"
        expect timeout {
          send_user " "
        } "Do you want to do NSM installation with base license? (y/n) *>" {
          send "y\r" 
          exp_continue
        } "Enter selection (1-2)*>" {
          send "2\r"
          exp_continue
        } "Will server(s) need to be reconfigured during the refresh? (y/n) *>" {
          send "n\r"
          exp_continue 
        } "Enter selection (1-3)*>" {
          send "3\r" 
          exp_continue
        } "Enter base directory location for management servers " {
          send "\r"
          exp_continue 
        } "Enable FIPS Support? (y/n)*>" {
          send "n\r"
          exp_continue
        } "Will this machine participate in an HA cluster? (y/n) *>" {
          send "n\r"
          exp_continue 
        } "Enter database log directory location *>" {
          send "\r"
          exp_continue
        } "Enter the management IP address of this server *>" {
          send "$ourip\r"
          exp_continue
        } "Enter the https port for NBI service *>" {
          send "\r"
          exp_continue
        } "Enter password (password will not display as you type)>" {
          send "$pass\r"
          exp_continue
        } "Will a Statistical Report Server be used with this GUI Server? (y/n) *>" {
          send "n\r"
          exp_continue
        } "UNIX password: " {
          send "$pass\r"
          exp_continue
        } "Will server processes need to be restarted automatically in case of a failure? (y/n) *>" {
          send "n\r"
          exp_continue
        } "Will this machine require local database backups? (y/n) *>" {
          send "n\r"
          exp_continue
        } "Enter Postgres DevSvr Db port *> " {
          send "\r"
          exp_continue
        } "Enter Postgres DevSvr Db super user *> " {
          send "\r"
          exp_continue
        } "Start server(s) when finished? (y/n) *> " {
          send "y\r"
          exp_continue
        } "Are the above actions correct? (y/n)> " {
          send "y\r"
          exp_continue
        }
    }

    \001u { 
      send "/etc/init.d/guiSvr stop\r"
      expect "*# " { send "/etc/init.d/haSvr stop\r"}
      expect "*# " { send "/usr/netscreen/GuiSvr/utils/setperms.sh GuiSvr > /dev/null\r"}
      expect "*# " { send "/usr/netscreen/GuiSvr/utils/.xdbUpdate.sh /usr/netscreen/GuiSvr/var/xdb admin 1 0 /__/password \"glee/aW9bOYEewkD/6Ri8sHh2mU=\" > /dev/null\r"}
      sleep 1
      expect "*# " { send "/usr/netscreen/GuiSvr/utils/.xdbUpdate.sh /usr/netscreen/GuiSvr/var/xdb server 0 0 /__/ip \"$ourip\" > /dev/null\r"}
      sleep 1
      expect "*# " { send "/usr/netscreen/GuiSvr/utils/.xdbUpdate.sh /usr/netscreen/GuiSvr/var/xdb server 0 1 /__/ip \"$ourip\" > /dev/null\r"}
      sleep 1
      expect "*# " { send "/usr/netscreen/GuiSvr/utils/.xdbUpdate.sh /usr/netscreen/GuiSvr/var/xdb shadow_server 0 1 /__/clientOneTimePassword \"dk2003ns\" > /dev/null\r"} 
      sleep 1
      set backuptime [ timestamp -format "%Y%m%d_%H%M%S"]
      expect "*# " { send "perl -npi\".old_$backuptime\" -e 's/ +/ /g;s/(clientOneTimePassword\\s+)\\S*/\$1 dk2003ns/i;s/(default.printLevel\\s+)\\S*/\$1 debug/i;s/(ourRsaPrivateKey|theirRsaPublicKey)/#\$1/i;s/(guiSvrDirectiveHandler.max.heap|devSvrDirectiveHandler.max.heap\\s+)\\d+/\$1 1536000000/i' /var/netscreen/*Svr/*Svr.cfg > /dev/null\r"}
      expect "*# " { send "/etc/init.d/haSvr restart\r"}
      expect "*# " { send "/etc/init.d/guiSvr restart\r"}
      expect "*# " { send "/etc/init.d/devSvr restart\r"}
    }
  }
}

set time     [ timestamp -format "%Y/%m/%d %H:%M:%S"]
send_log "\n---------- log close at $time ----------\n"
log_file
exec /bin/bzip2 /home/case/store/work/_archives_worklogs/$host-$filetime.log
exit

