#! /usr/bin/expect

proc vlan {sPort} {

set sConfig {
commit
set vlans vlan-id 1 l3-interface vlan-1
commit
set vlan-interface interface vlan-1
commit
set firewall filter f1 sequence 1 then action discard
commit
set firewall filter f1 sequence 1 from protocol tcp flags ack true
set firewall filter f1 sequence 1 from protocol tcp flags syn true
commit
set firewall filter f1 sequence 10 then action forward
commit
set firewall filter f1 output vlan-interface vlan-1
commit
delete firewall filter f1 output
commit
delete firewall filter f1
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
            "XorPlus\\$" {
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
                    "XorPlus#" {
                        send "$iCmd\r"
                        break
                    }
                }
            }
        }

            while 1 {
                expect {
                    "XorPlus#" {
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
