#!/usr/bin/expect --

#####################################
# repeat reboot on P3922
######################################
  set sUser admin
  set sPaw pica8
  set timeout -1
  set PX1 te-1/1/1
  
  spawn telnet 172.16.0.21 7014
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

