#!/usr/bin/ruby

# $Id$

require 'rubygems'
require 'snmp'

unless ARGV[0]
  puts "Please supply a starting hostname/ip"
  exit
end

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

  query = ["1.3.6.1.2.1.1.1","1.3.6.1.2.1.1.2","1.3.6.1.2.1.1.3","1.3.6.1.2.1.1.4","1.3.6.1.2.1.1.5","1.3.6.1.2.1.1.6","1.3.6.1.2.1.1.7",]
 
  gotanswer = 0

  snmpcommh.sort{|a,b| b[1]<=>a[1]}.each do |comm,value|
    puts "[+] host #{host} community #{comm}\n"
    
    manager = SNMP::Manager.new(:Host => host, :Version => :SNMPv2c, :Community => comm, :Timeout => 5, :Retries => 3)

    begin
      response = manager.get_bulk(0,1,query)
    rescue
      puts "[-] problem while connecting to host #{host}: #{$!}\n"
    end

    list = response.varbind_list

    if not list.empty? 
      list.each do |ans| 
        data.push(ans)
      end
      gotanswer = 1 
      snmpcommh[comm] += 1
      snmpcomm = comm
    end

    if gotanswer == 1 

      data.each do |item|
        puts "#{item.oid} - #{item.value}\n"
      end

      puts "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n"

      # next-hops and type of the route from the routing table
      query = ["1.3.6.1.2.1.4.24.4.1.4","1.3.6.1.2.1.4.24.4.1.7"]
   
      begin
          manager.walk(query) do |row| 
            if row[1].value >= 3
              puts "#{row[0].value}"
            else
              #puts "other #{row[0].value}"
            end
          end
      rescue
          puts "[-] problem while querying the host #{host}: #{$!}\n"
      end

      # IP addresses from the ARP table
      query = ["1.3.6.1.2.1.4.22.1.3"]

      rows = []      
      begin 
        manager.walk(query) do |row|
          row.each { |vb| puts "#{vb.value}\n" }
        end
      rescue
        puts "[-] problem while querying the host #{host}: #{$!}\n"
      end

      # my ips
      query = ["1.3.6.1.2.1.3.1.1.3"]
    
      rows = []
      begin
        manager.walk(query) do |row|
          row.each { |vb| puts "#{vb.oid} #{vb.value}\n" }
        end
      rescue
        puts "[-] problem while querying the host #{host}: #{$!}\n"
      end
 
      break if gotanswer == 1
    end
  end
end
