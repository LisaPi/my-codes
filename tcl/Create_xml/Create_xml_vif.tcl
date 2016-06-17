#!/usr/bin/expect --


set outfile [open vlan-vif.txt a]

set config_str "<vlan-interface xmlns=\"http://pica8.com/xorpplus/vlan-interface\">"
puts $outfile $config_str

set i 1
for {incr i 1} {$i <= 128} {incr i 1} {
set config_vlan "<loopback/><interface><name>vlan$i</name><vif><name>vlan$i</name><description/><address><name>192.168.$i.1</name><prefix-length>24</prefix-length></address></vif></interface>"
  puts $outfile $config_vlan
} 

set config_end "</vlan-interface>"
puts $outfile $config_end

close $outfile  