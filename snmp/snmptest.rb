#!/usr/bin/ruby

# $Id$

require 'rubygems'
require 'snmp'

unless ARGV[0]
  puts "Please supply a starting hostname/ip"
  exit
end

snmpcomma = ["public","private"]


# SNMP walking routine, with some added features
# delay after higher number of queries

def dowalk(mngr,query)

  rows = Array.new

  count = 0

  query.each do |oid|
    start_oid = SNMP::ObjectId.new(oid)
    next_oid = start_oid
    while next_oid.subtree_of?(start_oid)
      response = mngr.get_next(next_oid)
      varbind = response.varbind_list.first
      break if not varbind.oid.subtree_of?(start_oid)
      next_oid = varbind.oid
      count += 1
      # need to make this as a variable
      rows.push(varbind.value)
      sleep 0.1 if count >= 100
      break if count >= 1000
    end
  end

  rows
end

# rewriting array to hash to allow sorting of the community strings
# based on the hits we will have in the network
snmpcommh = Hash.new
snmpcomma.each { |comm| snmpcommh[comm] = 0 } 
snmpver = { "v1" => 0, "v2c" => 0 }
data = Array.new
hosts = Array.new

hosts.push(ARGV[0])

hosts.each do |host|

  query = ["1.3.6.1.2.1.1.1","1.3.6.1.2.1.1.2","1.3.6.1.2.1.1.3","1.3.6.1.2.1.1.4","1.3.6.1.2.1.1.5","1.3.6.1.2.1.1.6","1.3.6.1.2.1.1.7",]
 
  gotanswer = 0

  snmpcommh.sort{|a,b| b[1]<=>a[1]}.each do |comm,value|

    break if gotanswer == 1

    snmpver.sort{|a,b| b[1]<=>a[1]}.each do |ver,null|
      puts "[+] host #{host} community #{comm} version #{ver}"
      
      if ver == "v1"
        manager = SNMP::Manager.new(:Host => host, :Version => :SNMPv1, :Community => comm, :Timeout => 5, :Retries => 3)
      elsif ver == "v2c"
        manager = SNMP::Manager.new(:Host => host, :Version => :SNMPv2c, :Community => comm, :Timeout => 5, :Retries => 3)
      else
        puts "[-] SNMP version #{ver} not implemented"
        break
      end

      list = Array.new
      begin
        if ver == "v1"
          response = manager.get(query)
        else
          response = manager.get_bulk(0,1,query)
        end
        list = response.varbind_list
      rescue
        puts "[-] problem while connecting to host #{host}: #{$!}\n"
      end

      if not list.empty? 
        list.each do |ans| 
          data.push(ans)
        end
        gotanswer = 1 
        snmpcommh[comm] += 1
        snmpver[ver] += 1    
      end

      if gotanswer == 1 

        data.each do |item|
          puts "#{item.oid} - #{item.value}\n"
        end

        puts "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n"

        # next-hops and type of the route from the routing table
        query = ["1.3.6.1.2.1.4.24.4.1.4","1.3.6.1.2.1.4.24.4.1.7"]
        data = dowalk(manager,query)

        # we have two collums here, we are checking if any value 
        # in the second collumn is bigger or equal 3
        j=(data.length/2).to_i 
        (data.length/2).to_i.times { |i| puts data[i] if data[i+j] >=3 }
  
        # IP addresses from the ARP table
        query = ["1.3.6.1.2.1.4.22.1.3"]
        data = dowalk(manager,query)
        data.each {|item| puts "#{item}" }
  
        # my ips
        query = ["1.3.6.1.2.1.3.1.1.3"]
        data = dowalk(manager,query)
        data.each {|item| puts "#{item}" }    
   
        break if gotanswer == 1
      end
    end
  end
end
