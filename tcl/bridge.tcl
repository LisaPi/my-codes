#! /usr/bin/expect

proc vlan {sPort} {

set sConfig {
ovs-vsctl del-br br0
ovs-vsctl add-br br0 -- set bridge br0 datapath_type=pica8 
ovs-vsctl add-port br0 ge-1/1/1 vlan_mode=trunk tag=1 -- set Interface ge-1/1/1 type=pica8
ovs-vsctl add-port br0 ge-1/1/14 vlan_mode=trunk tag=1 -- set Interface ge-1/1/14 type=pica8
ovs-vsctl add-port br0 ge-1/1/25 vlan_mode=trunk tag=1 -- set Interface ge-1/1/25 type=pica8
ovs-vsctl add-port br0 ge-1/1/38 vlan_mode=trunk tag=1 -- set Interface ge-1/1/38 type=pica8
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
            "admin@PicOS-OVS\\$" {
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
