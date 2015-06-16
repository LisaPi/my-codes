#!/usr/bin/expect --
set icount 0

spawn telnet 10.10.50.123 2018
send "\r"

while 1 {

    while 1 {
        expect {
            "XorPlus login:" {
                send "root\r"
            }
            "Password:" {
                send "pica8\r"
            }
            "root@" {
                send "version\r"
                break
            }
        }
    }   

 foreach i {2.2} j {2.0.5} {
           incr icount 1
           puts "==== it is the $icount  time run==="

      while 1 {
            expect {
                "root@" {
                    send "sed -i s/$i/$j/g /etc/lsb-release\r"
                    puts "11111111111111111111111111"
                    break
                }
            }
        }    
           
      while 1 {
           expect {
               "#" {
                   send "reboot -f\r"
                   break
                }
            }
        }
 
    while 1 {
        expect {
             "Restarting system" {
                 send "\r"
                 break
                }
            }
        }     

      while 1 {
          expect {
              "Pica8 Auto Provisioning Tool" {
                  send "\r"
                  break
                }
            }
        }    
        
      while 1 {
           expect {
              -ex "Pica8 configuration provisioning system" {
              puts "222222222222222222222222222"
                   send "\r"
                   break
                }
            }
        }

        after 5000
     while 1 {
          expect {
             -ex "xorp_rtrmgr is running" {
             puts "33333333333333333333333333333"
                 send "\r"
                 break
                }
            }
        }   

         after 9000
     while 1 {
          expect {
             -ex "Stopping: PicOS L2/L3" {
             puts "44444444444444444444444444444444"
                 send "\r"
                 break
                }
            }
        }    

     while 1 {
          expect {
             -ex "Starting: PicOS Open vSwitch/OpenFlow." {
             puts "55555555555555555555555555555555"
                 send "\r"
                 break
                }
            }
        }            

     while 1 {
         expect {
            -ex "Pica8 configuration provisioning complete" {
            puts "666666666666666666666666666666666"
                send "\r"
                break
                }
            }
        }
        
      while 1 {
         expect {
             "PicOS-OVS login:" {
                 send "root\r"
             }
             "Password:" {
                 send "pica8\r"
             }
             "root@" {
                 send "picos_boot\r"
                 break
             }
         }
     }  

    while 1 {
       expect {
           -ex "Enter your choice" {
               send "1\r"
               break
            }
        }
    }

    while 1 {
        expect {
           -ex "root@" {
               send "/etc/init.d/picos restart\r"
                break
           }
        }
    }

    while 1 {
        expect {
            -ex "root@" {
                send "exit\r"
                break
            }
        }
    }

    puts "======================================"

        after 3000
    }

}


