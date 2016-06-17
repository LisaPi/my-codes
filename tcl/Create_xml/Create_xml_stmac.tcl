#!/usr/bin/expect --


set outfile [open staticmac.txt a]

set config_str "<interface xmlns=\"http://pica8.com/xorpplus/interface\">"
puts $outfile $config_str

#foreach h {0 1 2 3 4 5 6 7 8 9 A B C D E F} {
#  foreach i {0 1 2 3 4 5 6 7 8 9 A B C D E F} {
#    foreach j {0 1 2 3 4 5 6 7 8 9 A B C D E F} {
#      foreach k {0 1 2 3 4 5 6 7 8 9 A B C D E F} {
#       set config_vlan "<gigabit-ethernet><name>qe-1/1/2</name><description/><mtu>1514</mtu><speed>40000</speed><disable>false</disable><power-preemphasis-level>0</power-preemphasis-level><static-ethernet-switching><mac-address><mac>22:11:11:11:$h$i:$j$k</mac><vlan><id>1</id></vlan></mac-address></static-ethernet-switching><snmp-trap>true</snmp-trap></gigabit-ethernet>   "
#       puts $outfile $config_vlan
#       } 
#     }
#   }
#}

#set j 1
#for {incr j 1} {$j <= 128} {incr j 1} {
#foreach h {0 1 2 3 4 5 6 7 8 9 A B C D E F} {
# foreach i {0 1 2 3 4 5 6 7 8 9 A B C D E F} {
#       set config_vlan "<gigabit-ethernet><name>qe-1/1/2</name><description/><mtu>1514</mtu><speed>40000</speed><disable>false</disable><power-preemphasis-level>0</power-preemphasis-level><static-ethernet-switching><mac-address><mac>22:11:11:11:11:$h$i</mac><vlan><id>$j</id></vlan></mac-address></static-ethernet-switching><snmp-trap>true</snmp-trap></gigabit-ethernet>   "
#       puts $outfile $config_vlan
#      }
#   }
#}

foreach h {0 1 2 3 4 5 6 7 8 9 A B C D E F} {
 foreach i {0 1 2 3 4 5 6 7 8 9 A B C D E F} {
       set config_vlan "<gigabit-ethernet><name>qe-1/1/2</name><description/><mtu>1514</mtu><speed>40000</speed><disable>false</disable><power-preemphasis-level>0</power-preemphasis-level><static-ethernet-switching><mac-address><mac>22:11:11:11:11:$h$i</mac><vlan><id>2</id></vlan></mac-address></static-ethernet-switching><snmp-trap>true</snmp-trap></gigabit-ethernet>   "
       puts $outfile $config_vlan
      }
   }

set config_end "</interface>"
puts $outfile $config_end

close $outfile