#!/usr/bin/ruby

# $Id$

require 'rubygems'
require 'snmp'

unless ARGV[0]
  puts "Please supply a starting hostname/ip"
  exit
end

#query = ["sysContact.0","sysUpTime.0","sysDescr.0","sysName.0","sysLocation.0"]
query = ["sysDescr.0","sysName.0","sysUpTime.0"]
snmpcomma = ["public","private"]

# rewriting array to hash to allow sorting of the community strings
# based on the hits we will have in the network
snmpcommh = Hash.new
snmpcomma.each { |comm| snmpcommh[comm] = 0 } 

data = Array.new
hosts = Array.new

hosts.push(ARGV[0])

hosts.each do |host| 
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
        end
      end
    rescue
      puts "[-] problem while connecting to host #{host}: #{$!}\n"
    end
    break if gotanswer == 1
  end


  if gotanswer == 1 
#    1.upto(query.length) do |i|
#      puts "#{query[i-1]} - #{data[i-1]}\n"
    data.each do |val|
      puts "#{val}\n"
    end
  end
end
