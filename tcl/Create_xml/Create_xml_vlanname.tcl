#!/usr/bin/expect --


set outfile [open vlan-name.txt a]

set config_str "<vlans xmlns=\"http://pica8.com/xorpplus/vlans\">"
puts $outfile $config_str

set i 1
for {incr i 1} {$i <= 128} {incr i 1} {
set config_vlan " <vlan-id><id>$i\</id><description/><vlan-name>vlan$i</vlan-name><l3-interface>vlan$i</l3-interface></vlan-id> "
  puts $outfile $config_vlan
} 

set config_end "</vlans>"
puts $outfile $config_end

close $outfile



