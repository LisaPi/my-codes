#! /usr/bin/expect

proc vlan {sPort} {

set sConfig {
set vlans vlan-id 11
set vlans vlan-id 22
commit
set vlan-interface interface vlan-11 vif vlan-11 address 2001:1::1 prefix-length 64
set vlan-interface interface vlan-22 vif vlan-22-1 address 2002:1::1 prefix-length 64
set vlan-interface interface vlan-22 vif vlan-22-2 address 2002:2::1 prefix-length 64
set vlan-interface interface vlan-22 vif vlan-22-3 address 2002:3::1 prefix-length 64
set vlans vlan-id 11 l3-interface vlan-11
set vlans vlan-id 22 l3-interface vlan-22
commit
set interface aggregate-ethernet ae1 family ethernet-switching native-vlan-id 11
set interface aggregate-ethernet ae2 family ethernet-switching native-vlan-id 22
commit
set interface gigabit-ethernet te-1/1/1 ether-options 802.3ad ae1
set interface gigabit-ethernet te-1/1/14 ether-options 802.3ad ae2
commit
set protocols neighbour interface vlan-22 address 2002:1::100 mac-address 22:22:22:11:11:11
set interface aggregate-ethernet ae2 static-ethernet-switching mac-address 22:22:22:11:11:11 vlan 22
commit
set protocols neighbour interface vlan-22 address 2002:2::100 mac-address 22:22:22:22:22:22
set interface aggregate-ethernet ae2 static-ethernet-switching mac-address 22:22:22:22:22:22 vlan 22
commit
set protocols neighbour interface vlan-22 address 2002:3::100 mac-address 22:22:22:33:33:33
set interface aggregate-ethernet ae2 static-ethernet-switching mac-address 22:22:22:33:33:33 vlan 22
commit
delete protocols neighbour interface vlan-22
commit
delete interface gigabit-ethernet te-1/1/1 ether-options 802.3ad
delete interface gigabit-ethernet te-1/1/14 ether-options 802.3ad
commit
delete interface aggregate-ethernet ae1
delete interface aggregate-ethernet ae2
commit
delete vlan-interface interface vlan-11
delete vlan-interface interface vlan-22
commit
delete vlans vlan-id 11
delete vlans vlan-id 22
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
            "admin@XorPlus>" {
                send "configure\r"
                continue
            }
            "admin@XorPlus#" {
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
                    "admin@" {
                        send "$iCmd\r"
                        break
                    }
                }
            }
        }

            while 1 {
                expect {
                    "admin@" {
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

vlan $sPort
