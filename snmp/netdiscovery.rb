#!/usr/bin/ruby

# $Id$

require 'digest/md5'
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
      begin
        response = mngr.get_next(next_oid)
        varbind = response.varbind_list.first
      rescue
        puts "[-] error while quering for #{next_oid}"
        break
      end
      break if not varbind.oid.subtree_of?(start_oid)
      next_oid = varbind.oid
      count += 1

      # need to make below values as variables
      # we don't want to cause high CPU on the devices
      rows.push(varbind.value)
      if count >= 100
        sleep 0.1
        puts "[!] query count reached first limit - slowing down" if count == 100
      end
      if count >= 1000 
        puts "[!] query count reached second limit - stopping"
        break
      end
    end
  end

  rows
end

def hostquery(found,snmpcommh,snmpver,host) 

  data = Array.new
  neighbors = Hash.new

  # below we have standard OIDs that should be supported by almost all systems
  #  1.3.6.1.2.1.1.1 - sysDescr
  #  1.3.6.1.2.1.1.2 - sysObjectID
  #  1.3.6.1.2.1.1.3 - sysUpTime
  #  1.3.6.1.2.1.1.4 - sysContact
  #  1.3.6.1.2.1.1.5 - sysName
  #  1.3.6.1.2.1.1.6 - sysLocation
  #  1.3.6.1.2.1.1.7 - sysServices 

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
        puts "[-] problem while connecting to host #{host}: #{$!}"
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

        puts "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-"

        data.each do |item|
          puts "#{item.value}"
        end

        puts "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-"

        # my ips
        query = ["1.3.6.1.2.1.3.1.1.3"]
        data = dowalk(manager,query)
        data.each do |item| 
          puts "#{item}"
          found[item] = 1
        end    

        # md5 fingerprint of this host 
        # anyone has a better idea for filename ?
        md5 = Digest::MD5.hexdigest(data.to_s)
        puts md5   

        puts "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-"

        # next-hops and type of the route from the routing table
        query = ["1.3.6.1.2.1.4.24.4.1.4","1.3.6.1.2.1.4.24.4.1.7"]
        data = dowalk(manager,query)

        # we have two columns here, we are checking if any value 
        # in the second column is bigger or equal 3
        j = (data.length/2).to_i 
        (data.length/2).to_i.times do |i|
          if data[i+j] >= 3
            puts data[i]
            neighbors[data[i]] = 1
          end
        end
 
        puts "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-"
 
        # IP addresses from the ARP table
        query = ["1.3.6.1.2.1.4.22.1.3"]
        data = dowalk(manager,query)
        data.each do |item| 
          puts "#{item}"
          neighbors[item] = 1
        end
  
        break if gotanswer == 1
      end
    end
  end

  # now we will query neighbors
  # 
  neighbors.each do |neigh,val|
    next if (found.key?(neigh))
    hostquery(found,snmpcommh,snmpver,neigh)
  end 
end


# rewriting array to hash to allow sorting of the community strings
# based on the hits we will have in the network
snmpcommh = Hash.new
snmpcomma.each { |comm| snmpcommh[comm] = 0 } 
snmpver = { "v1" => 0, "v2c" => 0 }
found = Hash.new

hostquery(found,snmpcommh,snmpver,ARGV[0])

