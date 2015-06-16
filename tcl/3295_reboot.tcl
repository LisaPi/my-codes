#!/usr/bin/expect

log_file -noappend -a [pwd]/3295.log

proc rPdu {iPdu iPort} {

    # reload
    if {$iPdu == "92"} {

        spawn telnet 10.10.50.92
        send "\r"
        expect "Name"
        send "apc\r"
        expect "Password"
        send "apc\r"
        expect "Control Console"
        send "1\r"
        expect "Device Manager"
        send "2\r"
        expect "Outlet Management"
        send "1\r"
    } else {
        spawn telnet 10.10.50.90
        send "\r"
        expect "Name"
        send "apc\r"
        expect "Password"
        send "apc\r"
        expect "Control Console"
        send "1\r"
        expect "Device Manager"
        send "3\r"
    }

    while 1 {
        expect {
            "Press <ENTER> to continue" {
                send "\r"
            }
            "Master Control/Configuration" {
                break
            }
        }
    }

    while 1 {
        expect {
            ">" {
                send "$iPort\r"
                break
            }
        }
    }

    expect "Outlet"
    send "1\r"

    expect "Control Outlet"
    send "3\r"

    expect "Enter 'YES' to continue or <ENTER> to cancel :"
    send "yes\r"

    expect "Press <ENTER> to continue..."
    send "\r"

    while 1 {
        expect {
            "<ESC>- Back" {send \033; exp_continue}
            "Press <ENTER> to continue..." {send "\r"; exp_continue}
            "<ESC>- Main Menu" {send "4\r";break}
        }
    }
}

# Create port db
proc dbPort {sPort iPort sPro iPdu} {

    upvar $iPort iPorts
    upvar $sPro sPros
    upvar $iPdu iPdus

    after 5000
    spawn telnet 10.10.50.90

    while 1 {
        expect {
            "User Name" {
                send "apc\r"
            }
            "Password" {
                send "apc\r"
            }
            ">" {
                send "1\r"
                break
            }
        }
    }

    while 1 {
        expect {
            ">" {
                send "3\r\r"
                expect -re "(.*)Master Control"
                set sDbPort $expect_out(buffer)
                send "\r"
                break
            }
        }
    }

    expect "Press <ENTER> to continue..."
    send "\r"

    while 1 {
        expect {
            "<ESC>- Back" {send \033; exp_continue}
            "Press <ENTER> to continue..." {send "\r"; exp_continue}
            "<ESC>- Main Menu" {send "4\r";break}
        }
    }

    puts "\n########################"
    puts "sDbPort:$sDbPort\n"
    puts "########################\n"

    catch close

    regexp "(\[0-9]+)-\[ ]\\\[--]\[ ]+(\[0-9a-z]+)_\[0-9]_[set sPort]_" $sDbPort sTmp iPorts sPros

    if {[info exists iPorts] == 1} {
        set iPdus 90
        return
    }

    spawn telnet 10.10.50.92

    while 1 {
        expect {
            "User Name" {
                send "apc\r"
            }
            "Password" {
                send "apc\r"
            }
            ">" {
                send "1\r"
                break
            }
        }
    }

    while 1 {
        expect {
            ">" {
                send "2\r\r"
                break
            }
        }
    }

    while 1 {
        expect {
            ">" {
                send "1\r\r"
                expect -re "(.*)Master Control"
                set sDbPort $expect_out(buffer)
                send "\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "<ESC>- Back" {send \033; exp_continue}
            "Press <ENTER> to continue..." {send "\r"; exp_continue}
            "<ESC>- Main Menu" {send "4\r";break}
        }
    }

    puts "\n########################"
    puts "sDbPort:$sDbPort\n"
    puts "########################\n"

    catch close

    regexp "(\[0-9a-z]+)-\[ ]\\\[--]\[ ]+(\[0-9a-z]+)_\[0-9]_[set sPort]_" $sDbPort sTmp iPorts sPros
    set iPdus 92

    return
}

# Kill user
proc userKick {sPort} {

    spawn telnet 10.10.50.123

    while 1 {
        expect {
            "Username" {
                send "su\r"
            }
            "Local" {
                send "su override\r"
            }
            "Password" {
                send "system\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "Local" {
                send "logout port $sPort\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "Local" {
                send "logput\r"
                break
            }
        }
    }

    catch close
}

set sPort [lindex $argv 0]
if {$sPort == ""} {
    puts "Input err, please input console port!"
    exit
} else { 
    dbPort $sPort iPort sPro iPdu
}

after 5000
set timeout 30
userKick $sPort

set flag 0

for {set i 1} {$i > 0} {incr i} {

    puts "\n\nIt is the $i time to run, error time is $flag\n\n"
  
    rPdu $iPdu $iPort 
    after 2000
    spawn telnet 10.10.50.123 20$sPort
    send "\r"
 
    while 1 {
        expect {
            timeout {
                send "\r"
                rPdu $iPdu $iPort
            }
            "Booting" {
                send "\r"
                break
            }
         }
    }

    while 1 {
        expect {
           "linux_kernel_bde" {
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
            "assword" {
                send "pica8\r"
            }
            "XorPlus>" {
                send "\r"
                break
            }
        }
    }

    foreach tPort "te-1/1/49 te-1/1/50" {
        while 1 {
            expect {
                "XorPlus>" {
                    send "show interface gigabit-ethernet $tPort\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "Physical link is Down" {
                    incr flag
                    send "\r"
                    puts "====================stop================="
                    return 1
                    break
                }
                "Physical link is Up" {
                    send "\r"
                    break
                }
            }
        }
    }

    while 1 {
        expect {
            "XorPlus>" {
                send "\r"
                expect "*"
                match_max 10000
                expect -re ".+"
                send "\r"
                break
            }
        }
    }

    while 1 {
        expect {
           "XorPlus>" {
               send "exit\r"
               break
           }
        }
    }

    catch close
    catch wait

    after 5000
}
