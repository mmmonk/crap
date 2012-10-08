#!/usr/bin/expect -f

# $Id: 20121005$
# $Date: 2012-10-05 16:46:59$
# $Author: Marek Lukaszuk$

set user "root"
set pass "lab123"
set time_between_runs 30

set send_slow {5 .02}
set timeout 60

set time     [ timestamp -format "%Y/%m/%d %H:%M:%S"]
set filetime [ timestamp -format "%Y%m%d_%H%M%S"]

log_file "~/checksum_errors-$filetime.log"

set host [lindex $argv 0]

set firstrun 1

while { true } {

  set errorperhost 0

  if { $host != "" } {

    if { [regexp ":" $host] } {
      regexp {:(\S+)} $host match pass
      regexp {(\S+):} $host match host
    }

    if { [regexp "@" $host] } {
      regexp {(\S+?)@} $host match user
      regexp {@(\S+)} $host match host
    }

    spawn ssh $user@$host

    expect timeout {
      send_user "\n$host: CONNECTION ERROR - connection timeout\n"
      continue
    } eof {
      send_user "\n$host: CONNECTION ERROR - got eof\n"
      continue
    } "Login incorrect" {
      send_user "\n$host: CONNECTION ERROR - wrong credentials\n"
      continue
    } "Permission denied, please try again." {
      send_user "\n$host: CONNECTION ERROR - wrong credentials\n"
      continue
    } "Are you sure you want to continue connecting (yes/no)?" {
      send -s "yes\r"
      exp_continue
    } "ogin:" {
      send -s "$user\r"
      exp_continue
    } "assword:" {
      send -s "$pass\r"
      exp_continue
    } "*% " {
      send -s "\r"
    } "*> " {
      send -s "start shell\r"
      exp_continue
    }

    if { $firstrun == 1} {

      send_user "\n##### gathering baseline information #####"
      set firstrun 0

      expect "*% " { send -s "srx-cprod.sh -s spu -c show usp flow counters all | grep \"Cksum error\"\r"}
      expect "*% " { send -s "\r" }
      set buff $expect_out(buffer)
      regexp {\s(Cksum .+)@} $buff match ec1

      expect "*% " { send -s "srx-cprod.sh -s spu -c show usp cp flow counters | grep \"cksum error\"\r"}
      expect "*% " { send -s "\r" }
      set buff $expect_out(buffer)
      regexp {\s(cksum .+)@} $buff match ec2

      expect "*% " { send -s "srx-cprod.sh -s spu -c show nhdb management fabric | grep \"Receive IP Checksum Error\"\r"}
      expect "*% " { send -s "\r" }
      set buff $expect_out(buffer)
      regexp {\s(Receive .+)@} $buff match ec3
      set timeout 10
      send_user "\n##### starting main matching loop #####"
    }

    set OK1 1
    set OK2 1
    set OK3 1
    expect "*% " { send -s "srx-cprod.sh -s spu -c show usp flow counters all | grep \"Cksum error\"\r"}
    expect "$ec1" { set OK1 0 }
    expect "*% " { send -s "srx-cprod.sh -s spu -c show usp cp flow counters | grep \"cksum error\"\r"}
    expect "$ec2" { set OK2 0 }
    expect "*% " { send -s "srx-cprod.sh -s spu -c show nhdb management fabric | grep \"Receive IP Checksum Error\"\r"}
    expect "$ec3" { set OK3 0 }

    if { $OK1 == 1 || $OK2 == 1 || $OK3 == 1 } {
      # example alarm command
      set cmd "printf \"############################ "
      append cmd "ALARM $OK1 ###############################\" | xxd"
      system $cmd
    }

    expect "*% " { send -s "exit\r"}
    send_user "\n\n"
    close
    sleep $time_between_runs
  }
}
