#!/usr/bin/expect --
set icount 0
spawn telnet 10.10.50.123 2023 
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
                send "\r"
                break
            }
        }
    }

	set picos_spawn_id $spawn_id
	after 5000

    foreach i {12576 12555} j {12555 12576} {
           incr icount 1
           puts "==== it is the $icount  time run==="
	    spawn ssh root@10.10.50.47
    	while 1 {
            expect {
                "yes/no" {
                	send "yes\r"
            	}
            	"assword" {
                	send "pica8\r"
            	}
            	"root@" {
                	send "sed -i s/$i/$j/g /tftpboot/pica8/provision.script\r"
                    break
                }
            }
        }
   
        while 1 {
            expect {
                "root@" {
                    send "exit\r"
                    break
                }
           }
        }
 
        catch close

        after 1000
        set spawn_id $picos_spawn_id
        send "\r"
    
        while 1 {
            expect {
                "root@" {
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
               -ex "No start-up options for PicOS" {
               puts "222222222222222222222222222"
                   send "\r"
                   break
                }
            }
        }
        
      while 1 {
         expect {
             "XorPlus login:" {
                 send "root\r"
             }
             "Password:" {
                 send "pica8\r"
             }
             "root@" {
                 send "\r"
                 break
             }
         }
     }  

    puts "======================================"

        after 3000
    }

}


