proc arpmnk {} {

  set log [open "syslog:" w+]
  set arpall [exec "show arp"]
  foreach line [regexp -all -line -inline "^Internet .* Vlan1" $arpall] {
    set tokens [regexp -inline -all -- {\S+} $line] 
    set ip [lindex $tokens 1]
    set mac [lindex $tokens 3]
    set txt [concat "%ARP-7-MONKEY:" $ip " " $mac] 
    puts $log $txt
  }
  close $log
}
