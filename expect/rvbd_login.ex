#!/usr/bin/expect -f

# $Id: 20130410$
# $Date: 2013-04-10 13:34:30$
# $Author: Marek Lukaszuk$

# ver: 20120403

proc curtime { } {
  return [ timestamp -format "%Y/%m/%d %H:%M:%S"]
}

proc backuptimeproc { } {
  return [ timestamp -format "%Y%m%d_%H%M%S"]
}

proc online_help {} {
      send_user "
--- Help ---

Ctrl+a h - this message,
Ctrl+a ? - also this message ;),
Ctrl+a s - shell access
"
      send "\r"
}


if {[info exists env(LOGIN_ARCH)]} {
  set logdir "$env(LOGIN_ARCH)"
} else {
  set logdir "$env(HOME)/store/work/_archives_worklogs/"
}

set send_slow {10 .1}
set timeout 90

if { $argc == 0 } {
  puts "
Usage: $argv0 <username@>host <password>

If not specified username defaults to \"admin\" and password to \"password\".

The connection to target host is done with normal ssh command without any arguments.
My suggestion is to use ~/.ssh/config for any non standard options.
"
  exit
} else {
  set host [lindex $argv 0]
  set user "admin"
  set pass "password"
  if { [regexp @ $host] } {
    regexp {(\S+?)@} $host match user
    regexp {@(\S+)} $host match host
  }
  if { $argc > 1 } {
    set pass [lindex $argv 1]
  }
}

spawn ssh -q -o "ControlPersist no" $user@$host

set stime    [ timestamp -format "%Y/%m/%d %H:%M:%S"]
set filetime [ timestamp -format "%Y%m%d_%H%M%S"]

send -s "\r"

expect timeout {
  send_user "connection timeout\n"
  exit

} eof {
  send_user "got eof\n"
  exit

} "Are you sure you want to continue connecting" {
  send -s "yes\r"
  exp_continue

} "ogin incorrect" {
  send_user "wrong credentials\n"
  exit

} "assword:" {
  send -s "$pass\r"
  exp_continue

} -re " > $" {
  send -s "en\r"
  exp_continue

} " # " {
  send -s "cli session auto-logout 0\r"
}

expect -re ".*(%|>|#) " {
  log_file "$logdir/$host-$filetime.log"
  send_log "\n---------- log start at $stime ----------\n"

  send_user "
--- Help key ---
Ctrl+a h - all shortcuts

"
  send "\r"

  interact {

    \003  { send "\003" }
    \004  {
      send "\r"
      expect "# " {
        send -s "exit\r"
        exp_continue
      } " > " {
        send -s "exit\r"
      }
      wait
      exit
    }

    \001s {
      send -s "cli challenge generate\r"
      expect -re "Generated challenge: .+\n" {
        set challenge ""
        regexp -line {Generated challenge: (.+?)$} $expect_out(buffer) m challenge
        set response [ exec ~/bin/rvbd.py -e $challenge]
        set cmd ""
        regexp -line {cmd: (.+?)$} $response m cmd
        send -s "$cmd\r"
      }
      expect "Verification succeeded." { send -s "_shell\r" }
    }

    \001h {
      online_help
    }

    \001? {
      online_help
    }

#    \001x {
#      send_user "\nType the action (stop/status/start/restart/version):"
#      stty cooked echo
#      expect_user -re "(.*)\n"
#      stty raw -echo
#      set action $expect_out(1,string)
#      send -s "/etc/init.d/guiSvr $action; /etc/init.d/devSvr $action; /etc/init.d/haSvr $action\n"
#    }
#
#    \001d {
#      send -s "cd /usr/netscreen/GuiSvr/utils/ && ./debugConsole\n"
#
#      expect "Server mgtsvr is now connected phase" { send -s "\n" }
#
#      expect "relay>" {
#        send -s "mgtsvr\n"
#      } "*#" {
#        send -s "\n"
#      }
#
#      expect "mgtsvr>" {
#        send -s "set printer levels debug\n"
#      } "No command" {
#        send -s "devsvr\n"
#      } "*#" {
#        send -s "\n"
#      }
#
#      expect "mgtsvr>" {
#        send -s "devsvr\n"
#        exp_continue
#      } "devsvr>" {
#        send -s "set printer levels debug\n"
#      } "No command" {
#        send -s "\n"
#      } "*#" {
#        send -s "\n"
#      }
#
#      expect "mgtsvr>" {
#        send -s "local\n"
#        exp_continue
#      } "devsvr>" {
#        send -s "local\n"
#        exp_continue
#      } "relay>" {
#        send -s "quit really\n"
#      } "*#" {
#        send -s "\n"
#      }
#
#      expect "*#" { send -s "/usr/netscreen/GuiSvr/utils/guiSvrCli.sh --gdh-debug --debug\n"}
#      expect "*#" { send -s "/usr/netscreen/DevSvr/utils/devSvrCli.sh --ddh-debug --debug\n"}
#
#    }
#    \001t {
#      send -s [backuptimeproc]
#    }

#    \001c {
#      send_user "\nType the action number:
# 1 - correct /usr/netscreen/DevSvr/var/devSvr.cfg by removing unneeded white characters (make a copy) and restart DevSvr,
# 2 - truncate the schema,
# 3 - correct the customer db (super password, IPs),
# 4 - prepare a command that will uninstall all NSM packages and remove all the NSM data from the server, the command is printed without \\r at the end,
# 5 - print the command needed to export the db to xdif ($filetime),
# 6 - print the command needed to import the db from xdif ($filetime),
# 7 - disables encryption between devSvr and the devices,
#
# input: "
#      stty cooked echo
#      expect_user -re "(.*)\n"
#      stty raw -echo
#      set action $expect_out(1,string)
#
#      send "\r"
#
#      # devsvr.cfg corrections of whitespaces
#      if { $action == 1 } {
#        send "/etc/init.d/devSvr stop; perl -pi\".[backuptimeproc]\" -e 's/  +/ /g' /usr/netscreen/DevSvr/var/devSvr.cfg && /etc/init.d/devSvr start\r"
#
#      # truncate schema
#      } elseif { $action == 2 } {
#        send -s "history -w ~/.bash_history\r"
#        expect "*# " { send -s "/etc/init.d/haSvr stop\r"}
#        expect "*# " { send -s "/etc/init.d/guiSvr stop\r"}
#        expect "*# " { send -s "/etc/init.d/devSvr stop\r"}
#        #expect "*# " { send -s "mv -f /usr/netscreen/GuiSvr/var/dmi-schema-stage /usr/netscreen/GuiSvr/var/dmi-schema-stage.old\r"}
#        expect "*# " { send -s "rm -rf /usr/netscreen/GuiSvr/var/dmi-schema-stage\r"}
#        expect "*# " { send -s "cp --reply=yes -fpr /usr/netscreen/GuiSvr/lib/initVar/dmi-schema-stage /usr/netscreen/GuiSvr/var/dmi-schema-stage\r"}
#        expect "*# " { send -s "rm -f /usr/netscreen/GuiSvr/var/xdb/init/*\r"}
#        expect "*# " { send -s "rm -rf /tmp/Schemas*\r"}
#        expect "*# " { send -s "rm -rf /usr/netscreen/GuiSvr/var/Schemas-GDH/*\r"}
#        expect "*# " { send -s "sh /usr/netscreen/GuiSvr/utils/.truncateSchemaTables.sh /usr/netscreen/GuiSvr/var/xdb\r"}
#        expect "*# " { send -s "cp --reply=yes -fpr /usr/netscreen/GuiSvr/lib/initVar/xdb/init/* /usr/netscreen/GuiSvr/var/xdb/init/\r"}
#        expect "*# " { send -s "history -r ~/.bash_history\r"}
#
#      # correct the customer db (super password, IPs)
#      } elseif { $action == 3 } {
#        send -s "history -w ~/.bash_history\r"
#        expect "*# " { send -s "/etc/init.d/haSvr stop\r"}
#        expect "*# " { send -s "/etc/init.d/devSvr stop\r"}
#        expect "*# " { send -s "/etc/init.d/guiSvr stop\r"}
#        expect "*# " { send -s "/usr/netscreen/GuiSvr/utils/setperms.sh GuiSvr > /dev/null\r"}
#        expect "*# " { send -s "/bin/chmod +s /usr/netscreen/GuiSvr/utils/.installIdTool\r"}
#        expect "*# " { send -s "/usr/netscreen/GuiSvr/utils/.xdbUpdate.sh /usr/netscreen/GuiSvr/var/xdb admin 1 0 /__/password \"glee/aW9bOYEewkD/6Ri8sHh2mU=\" > /dev/null\r"}
#        sleep 1
#        expect "*# " { send -s "/usr/netscreen/GuiSvr/utils/.xdbUpdate.sh /usr/netscreen/GuiSvr/var/xdb server 0 0 /__/ip \"$ourip\" > /dev/null\r"}
#        sleep 1
#        expect "*# " { send -s "/usr/netscreen/GuiSvr/utils/.xdbUpdate.sh /usr/netscreen/GuiSvr/var/xdb server 0 1 /__/ip \"$ourip\" > /dev/null\r"}
#        sleep 1
#        expect "*# " { send -s "/usr/netscreen/GuiSvr/utils/.xdbUpdate.sh /usr/netscreen/GuiSvr/var/xdb shadow_server 0 1 /__/clientOneTimePassword \"dk2003ns\" > /dev/null\r"}
#        sleep 1
#        expect "*# " { send -s "perl -npi\".old_[backuptimeproc]\" -e 's/ +/ /g;\
#        s/(clientOneTimePassword\\s+)\\S*/\$1 dk2003ns/i;\
#        s/(default.printLevel\\s+)\\S*/\$1 debug/i;\
#        s/(ourRsaPrivateKey|theirRsaPublicKey)/#\$1/i;\
#        s/(guiSvrDirectiveHandler.max.heap|devSvrDirectiveHandler.max.heap\\s*) \\d+/\$1 1536000000/i' /var/netscreen/*Svr/*Svr.cfg > /dev/null;\
#        perl -i -pe 's/(^gzip|^tar)/#\$1/' /usr/netscreen/GuiSvr/utils/xdifImporter.sh;\
#        history -r ~/.bash_history\r"}
#
#      # NSM removal
#      } elseif { $action == 4 } {
#        if { $os == "Linux" } {
#          send -s "rpm -qa | grep netscreen | xargs -r rpm -e ; rm -rf /var/netscreen/*/* /usr/netscreen/*"
#        } elseif { $os == "SunOS" } {
#          send -s "pkgrm -n `pkginfo -c application | grep -i netscreen | grep -v NSCNpostgres | awk '{print \$2}' | xargs` &&  rm -rf /var/netscreen/ /usr/netscreen/"
#        }
#      } elseif { $action == 5 } {
#        send -s "unset NS_PRINTER_LEVEL;/usr/netscreen/GuiSvr/utils/xdbExporter.sh /var/netscreen/GuiSvr/xdb/ /var/tmp/xdif_$filetime.txt; export NS_PRINTER_LEVEL=debug"
#
#      } elseif { $action == 6 } {
#        send -s "/usr/netscreen/GuiSvr/utils/xdifImporter.sh /var/tmp/xdif_$filetime.txt /var/netscreen/GuiSvr/xdb/init/ "
#
#      } elseif { $action == 7 } {
#        send -s "/etc/init.d/devSvr stop; perl -pi\".[backuptimeproc]\" -e 's/(devSvrManager.cryptoKeyLength\\s*) \\d+/\$1 0/' /usr/netscreen/DevSvr/var/devSvr.cfg && /etc/init.d/devSvr start\r"
#
#      # default - unknown choice
#      } else {
#        send_user "\nUnknown choice\n"
#      }
#    }

    \001l {
      send "\r"
      expect " > " {
        send -s "en\r"
        exp_continue
      } "# " {
        send -s "\r"
      }
    }
  }
}

set time     [ timestamp -format "%Y/%m/%d %H:%M:%S"]
send_log "\n---------- log close at $time ----------\n"
log_file
exec /bin/bzip2 $logdir/$host-$filetime.log
send_user "\n\[+\] session lasted from $stime to $time\n\[+\] logfile: $logdir/$host-$filetime.log.bz2\n"
exit

