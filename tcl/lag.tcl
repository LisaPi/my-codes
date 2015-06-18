#! /usr/bin/expect

proc vlan {sPort} {

set sConfig {
set interface aggregate-ethernet ae1
set interface gigabit-ethernet ge-1/1/1 ether-options 802.3ad ae1 
commit
delete interface gigabit-ethernet ge-1/1/1 ether-options 802.3ad
commit
delete interface aggregate-ethernet ae1
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
