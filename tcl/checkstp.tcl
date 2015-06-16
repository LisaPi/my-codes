#!/usr/bin/expect --

#####################################
# Using PDU to control
######################################
proc rPdu {iPdu iPort} {

    # reload
    if {$iPdu == "91" || $iPdu == "92" || $iPdu == "93"} {

        spawn telnet 10.10.50.$iPdu
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
    send "2\r"

    expect "Enter 'YES' to continue or <ENTER> to cancel :"
    send "yes\r"

    expect "Press <ENTER> to continue..."
    send "\r"
    
    expect "Control Outlet"
    send "1\r"

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

#####################################
# repeat reboot and check the spanning-tree status on P3922
######################################
  set sUser admin
  set sPaw pica8
  set timeout -1
  set PX1 te-1/1/1
  set iPdu 90 
  set iPort 22
  
  spawn telnet 10.10.50.123 2026
  send "\r"    

  for {set i 1} {$i<=10} {incr i} {
    puts "===\n\nIt is the $i time to run\n\n==="
    expect "$sUser@"
    send "exit\r"
    expect "login:"
    send "$sUser\r"
    expect "assword:"
    send "$sPaw\r"
    while 1 {
        expect {
         "$sUser@" {
             send "version\r"
             break
           }       
         }
      } 

    while 1 {
        expect {
         "$sUser@" {
             send "cli\r"
             break
           }       
         }
      } 
   after 5000
    while 1 {
        expect {
            -ex "XorPlus>" {
                send "show spanning-tree statistics interface $PX1\r"
                expect -re "$PX1"
                send "\r"
                break
            }
        }
    }
    
    after 9000
    while 1 {
        expect {
            "XorPlus>" {
                send "show interface gigabit-ethernet $PX1\r"
                expect -re "Output Octets"
                send "\r"
                regexp {Output Packets...........................([0-9]+)} $expect_out(buffer) sTmp sNum
                puts $sNum
                break
            }
         }
      } 
      
    if {$sNum==0} {
     set flag 1
     puts "Running the $i time, the switch is not working normally!"
     return
    }  
    
    while 1 {
        expect {
            -ex "XorPlus>" {
                send "request system reboot\r"
                break
            }
        }
    }
    
    while 1 {
        expect {
            -ex "PCIE Test ...................... FAIL" {
                send "\r"
                rPdu $iPdu $iPort
            }
            "Hit any key to stop autoboot" {
                send "\r"
                break
            }
         }
    }  
    
    set timeout -1
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
                send "$sUser\r"
            }
            "Password:" {
                send "$sPaw\r"
                break
             }
        }
    }
 
     while 1 {
         expect {
          "$sUser@" {
              send "\r"
              break
            }       
          }
       }  
    puts "======================================"

}

