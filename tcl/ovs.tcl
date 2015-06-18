#! /usr/bin/expect

proc vlan {sPort} {

set sConfig {
ovs-vsctl del-br br
}
    set timeout 15
    spawn ssh 10.10.51.150 -l admin

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

            for {set i 0} {$i < 500} {incr i} {
            while 1 {
                expect {
                    "admin@" {
                        send "$iCmd$i\r"
                        break
                    }
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
