#!/usr/bin/expect --
spawn telnet 10.10.50.123 2033
send "\r"

set i 0
while 1 {

    incr i
    puts "It is the $i time to run!"

    while 1 {
        expect {
            "ogin:" {
                send "admin\r"
            }
            "assword" {
                send "pica8\r"
            }
            "admin@" {
                send "sudo reboot -f\r"
                break
            }
        }
    }    
}
