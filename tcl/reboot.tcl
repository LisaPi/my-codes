#! /usr/bin/expect

proc vlan {sPort} {

set sConfig {
sudo reboot -f
}
    set timeout 15
    spawn telnet 10.10.50.123 20$sPort

    send "\r"
    while 1 {
        expect {
            "login:" {
                send "admin\r"
                continue
            }
            "assword:" {
                send "pica8\r"
                continue
            }
            "XorPlus\\$" {
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
                    "XorPlus\\$" {
                        send "$iCmd\r"
                        break
                    }
                }
            }
        }

            while 1 {
                expect {
                    "Starting bootloader" {
                        send "\r"
                        break
                    }
                }
            }


            while 1 {
                expect {
                    "XorPlus login:" {
                        send "admin\r"
                    }
                    "assword:" {
                        send "pica8\r"
                    }
                    "XorPlus\\$" {
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
