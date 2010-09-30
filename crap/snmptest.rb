#!/usr/bin/ruby

# $Id$

require 'rubygems'
require 'snmp'

unless ARGV[0]
  puts "Please supply a starting hostname/ip"
  exit
end

query = Array.new 
snmpcomm = ""
snmpcomma = ["public","private"]

# rewriting array to hash to allow sorting of the community strings
# based on the hits we will have in the network
snmpcommh = Hash.new
snmpcomma.each { |comm| snmpcommh[comm] = 0 } 

data = Array.new
hosts = Array.new

hosts.push(ARGV[0])

hosts.each do |host|

  query = ["sysContact.0","sysUpTime.0","sysDescr.0","sysName.0","sysLocation.0"]
 
  gotanswer = 0
  snmpcommh.sort{|a,b| b[1]<=>a[1]}.each do |comm,value|
    puts "[+] host #{host} community #{comm}\n"
    
    begin
      SNMP::Manager.open(:Host => host, :Version => :SNMPv2c, :Community => comm, :Timeout => 5, :Retries => 3) do |manager| 
        response = manager.get_bulk(0,1,query)
        list = response.varbind_list

        if not list.empty? 
          list.each do |ans| 
            data.push(ans)
          end
          gotanswer = 1 
          snmpcommh[comm] += 1
          snmpcomm = comm
        end
      end
    rescue
      puts "[-] problem while connecting to host #{host}: #{$!}\n"
    end
    break if gotanswer == 1
  end

  if gotanswer == 1 
    data.each do |item|
      puts "#{item.oid} - #{item.value}\n"
    end
  end

  puts "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n"

  # next-hops from the routing table
  query = ["1.3.6.1.2.1.4.24.4.1.4","1.3.6.1.2.1.4.24.4.1.7"]

  begin
    SNMP::Manager.open(:Host => host, :Version => :SNMPv2c, :Community => snmpcomm, :Timeout => 5, :Retries => 3) do |manager|
      manager.walk(query) do |row|
        puts "#{row[0].value}" if row[1].value >= 3 
      end

      # IP addresses from the ARP table
      query = ["1.3.6.1.2.1.4.22.1.3"]
      
      manager.walk(query) do |row|
        row.each { |vb| puts "#{vb.value}\n" }
      end
    end
  rescue
    puts "[-] problem while querying the host #{host}: #{$!}\n"
  end
end
