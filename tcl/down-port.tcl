#!/usr/bin/expect --

spawn telnet 10.10.51.167

    while 1 {
        expect {
            "login" {
                send "admin\r"
            }
            "assword" {
                send "pica8\r"
            }
            "admin@" {
                send "cli \r"
                break
            }
        }
    }

    while 1 {
        expect {
            "XorPlus>" {
                send "configure\r"
                break
            }
        }
    }

while 1 {
	foreach i {ge-1/1/19  ge-1/1/21 ge-1/1/1 ge-1/1/19 ge-1/1/21 ge-1/1/1} j { true   true true   false  false false} {

    	while 1 {
            expect {
                "XorPlus#" {
                    send "set interface gigabit-ethernet $i disable $j\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "XorPlus#" {
                    send "commit\r"
					break
                }
            }
        }

        while 1 {
            expect {
                "Commit OK" {
                    send "\r"
                    break
                }
            }
        }
   
        after 9000
	}
}
