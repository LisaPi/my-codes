#! /usr/bin/expect

proc cli {sPort} {

set sConfig {
set vlans vlan-id 2
set vlans vlan-id 4
set vlans vlan-id 3 l3-interface vlan3  
set vlans vlan-id 5 l3-interface vlan5  
set vlans vlan-id 6 l3-interface vlan6  
set vlans vlan-id 7 l3-interface vlan7  
set vlans vlan-id 100 l3-interface vlan100  
set vlans vlan-id 200 l3-interface vlan200  
commit
set vlan-interface interface vlan3 vif vlan3 address 38.64.191.65 prefix-length 26
set vlan-interface interface vlan3 vif vlan3 address 2605:a680:ffff:0001::1 prefix-length 64
set vlan-interface interface vlan5 vif vlan5 address 38.64.188.1 prefix-length 24
set vlan-interface interface vlan5 vif vlan5 address 2605:a680:000f:1::1 prefix-length 64
commit
set vlan-interface interface vlan6 vif vlan6 address 38.64.189.1 prefix-length 24
set vlan-interface interface vlan6 vif vlan6 address 2605:a680:000f:2::1 prefix-length 64
set vlan-interface interface vlan7 vif vlan7 address 38.64.190.1 prefix-length 24
set vlan-interface interface vlan7 vif vlan7 address 2605:a680:000f:3::1 prefix-length 64
commit
set vlan-interface interface vlan100 vif vlan100 address 38.64.191.194 prefix-length 30
set vlan-interface interface vlan100 vif vlan100 address 2605:a680:ffff:ffff::2 prefix-length 64
set vlan-interface interface vlan200 vif vlan200 address 38.88.240.114 prefix-length 30
set vlan-interface interface vlan200 vif vlan200 address 2001:550:2:8::36:2 prefix-length 112
commit
set interface gigabit-ethernet ge-1/1/17 family ethernet-switching native-vlan-id 2
set interface gigabit-ethernet ge-1/1/19 family ethernet-switching port-mode trunk
set interface gigabit-ethernet ge-1/1/19 family ethernet-switching vlan members 3,5,6,7
set interface gigabit-ethernet ge-1/1/29 family ethernet-switching port-mode trunk
set interface gigabit-ethernet ge-1/1/29 family ethernet-switching vlan members 6
set interface gigabit-ethernet ge-1/1/31 family ethernet-switching port-mode trunk
commit
set interface gigabit-ethernet ge-1/1/31 family ethernet-switching vlan members 5,6,7
set interface gigabit-ethernet ge-1/1/33 family ethernet-switching native-vlan-id 2
set interface gigabit-ethernet ge-1/1/34 family ethernet-switching native-vlan-id 2
set interface gigabit-ethernet ge-1/1/36 family ethernet-switching native-vlan-id 2
set interface gigabit-ethernet ge-1/1/38 family ethernet-switching native-vlan-id 2
set interface gigabit-ethernet ge-1/1/48 family ethernet-switching native-vlan-id 2
set interface gigabit-ethernet te-1/1/49 family ethernet-switching native-vlan-id 200
set interface gigabit-ethernet te-1/1/50 family ethernet-switching native-vlan-id 3
set interface gigabit-ethernet te-1/1/51 family ethernet-switching port-mode trunk
set interface gigabit-ethernet te-1/1/51 family ethernet-switching vlan members 2
commit
set protocols spanning-tree enable false  
set protocols snmp community d0tt0M!B 
set protocols snmp trap-group targets 38.64.191.68
commit
set protocols static route 0.0.0.0/0 next-hop 38.88.240.113
set protocols static route 38.64.191.0/27 next-hop 38.64.191.193
set protocols static route 38.64.191.196/30 next-hop 38.64.191.193
set protocols static route 38.64.191.200/30 next-hop 38.64.191.193
set protocols static route 38.64.191.204/30 next-hop 38.64.191.193
set protocols static route 38.64.191.208/30 next-hop 38.64.191.193
set protocols static route 38.64.191.212/30 next-hop 38.64.191.193
set protocols static route 2605:a680:1:ff00::/56 next-hop 2605:a680:f:2:1111::8c50
set protocols static route 2605:a680:1:fe00::/56 next-hop 2605:a680:f:2:1111::a3ff
set protocols static route ::/0 next-hop 2001:550:2:8::36:1
set protocols static route 2605:a680:ffff:fffe::/64 next-hop 2605:a680:ffff:ffff::1
set protocols static route 2605:a680:0010::/44 next-hop 2605:a680:ffff:ffff::1
commit
set system ntp-server-ip 206.108.0.13
set system snmp-acl network 10.1.1.0/24
set system timezone America/Toronto
commit
set protocols ipfix collector 38.64.191.71 udp-port 2055
set protocols ipfix interfaces egress te-1/1/49
set protocols ipfix interfaces ingress te-1/1/49
commit
}
    set timeout 15
    spawn telnet 10.10.50.123 20$sPort

    send "\r"
    while 1 {
        expect {
            "password:" {
                send "pica8\r"
                continue
            }
            "admin@XorPlus\\$" {
                send "cli\r"
                continue
            }
            "XorPlus>" {
                send "configure\r"
                continue
            }
            "XorPlus#" {
                send "\r"
                break
            }
        }
    }

    while 1 {
    
        foreach iCmd [split $sConfig \r\n] {
            if {$iCmd == ""} {
                continue            
            }
            while 1 {
                expect {
                    "#" {
                        send "$iCmd\r"
                        break
                    }
                }
            }
        }

            while 1 {
                expect {
                    "#" {
                        send "\r"
                        break
                    }
                }
            }

    }

}

set sPort [lindex $argv 0]
if {$sPort == ""} {
    puts "Please input console port (eg, 05)!"
    exit
}

cli $sPort
