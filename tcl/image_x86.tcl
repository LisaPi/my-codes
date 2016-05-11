#!/usr/bin/expect --

########################
#get the latest version installer.bin 
########################
proc GetInstallerImage {sIp sPo sIm {sVer 0}} {

    upvar $sIm sIms
    set sDir daily
    set timetout 5
    global onie_name
    global onie_format
    global dir_name
    
    #onie foramt  mapping  
    set onie_name [dict create "2632" "im_niagara2632xl" \
                                 "2948" "im_niagara2948_6xl" \
                                 "5712" "*5712*" \
                                 "671232" "*6712*" \
                                 "7032" "inventec_dcs7032q28" ]
    
    
    #onie platform foramt  mapping 
    set onie_format  [dict create   "2632" "x86" \
                                  "2948" "x86" \
                                  "5712" "x86" \
                                  "671232"  "x86"\
                                  "7032" "x86" ]

    #box dir mapping  
    set dir_name [dict create "2632" "niagara2632xl" \
                                    "2948" "niagara2948_6xl" \
                                    "5712" "as5712_54x" \
                                    "671232" "as6712_32x" \
                                    "7032" "dcs7032q28" ]
                                      
    set sPro [dict get $dir_name $sPo ]                               
    set oBox  [dict get $onie_format  $sPo ] 
    set Onie  [dict get $onie_name  $sPo ] 
    
    spawn ssh $sIp -l build
    while 1 {
        expect {
            "yes/no" {
                send "yes\r"
            }
            "password:" {
                send "build\r"
                break
            }
        }
    }
    expect "build@"
    set timeout -1
    send "cd /tftpboot/build/$sDir/$sPro\r"
    expect "build@"
    if {$sVer == 0} {
        send "ls -lt onie-installer-$oBox-$Onie*.bin\r"
        expect -re "(rw\[^\r]*)\r\n"
        regexp "(onie-installer-$oBox-\[_0-9a-zA-Z]+-picos-\[0-9.a-zA-Z]+(\[-a-zA-Z0-9.]+)?.bin)" $expect_out(buffer) sTmp sIms
    } else {
        send "ls -lt onie-installer-$oBox-$Onie*$sVer*.bin\r"
        expect -re "(rw\[^\r]*)\r\n"
        regexp "(onie-installer-$oBox-\[_0-9a-zA-Z]+-picos-\[0-9.a-zA-Z]+(\[-a-zA-Z0-9.]+)?.bin)" $expect_out(buffer) sTmp sIms
    }
    send "exit\r"
    expect "logout"
    catch close
    catch wait

    set sIms "build/$sDir/$sPro/$sIms"
    puts  "The installer image location for $sPro is: $sIms\n\n"

    return 
}


###### Check get new or specific image
proc sCheck {sVer} {

	upvar $sVer sVers

	set timeout 15
       send_user "The latest Image (input 0); specific image (input 1):"
       expect_user {
    	-re "0\n" {set flag 0}
    	-re "1\n" {set flag 1}
    	timeout {set flag 0}
        -re "\n" {set flag 0}
	}

	if {$flag == 1} {
	    set timeout 60

    	while 1 {
        	send_user "The image's Revision number: "
        	expect_user {
            	-re "(\[0-9]+)\n" break
            	-re (.*)\n {
                	send_error "input error!"
            	}
            	timeout {
                	send_error "Wait too longer, exit!\n"
                	exit
            	  }
        	}
    	}

	   set sVers $expect_out(1,string)
	} elseif {$flag == 0} {

	   set sVers 0
	} else {

        set timeout 60

        while 1 {
            send_user "Directory: "
            expect_user {
                -re (.*)\n {
                    break
                }
                timeout {
                    send_error "Wait too longer, exit!\n"
                    exit
                }
            }
        }

        set sVers $expect_out(1,string)
    }

	return
}

###### Kill user on 50.122 console port
proc userKick {sPort} {

    spawn telnet 10.10.50.122

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
    catch wait
}

###### Kill user on 50.123 console port
proc userKickNew {sPort} {

    spawn ssh 10.10.50.123 -l root

    while 1 {
        expect {
            "yes/no" {
                send "yes\r"
            }
            "assword:" {
                send "tslinux\r"
            }
            "root@" {
                send "CLI\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "Enter your choice:" {
                send "cancel\r"
            }
            "cli>" {
                send "administration\r"
            }
            "administration>" {
                send "sessions\r"
            }
            "sessions>" {
                send "kill $sPort\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "sessions>" {
                send "quit\r"
            }
            "root@" {
                send "exit\r"
                break
            }
        }
    }

    catch close
    catch wait
}

###### Kill pdu
proc pduKill {iPdu} {

	foreach sIp {10.10.50.16 10.10.51.16} {
       spawn ssh root@$sIp

       expect {
	    "yes/no" {
		  send "yes\r"
	    }
           "assword" {
                send "pica8\r"
           }
            "root@" {
                send "kill \$(ps aux|grep \"$iPdu\"|awk '{print \$2}')\r"
            }
	  }

            expect {
                "root@" {
                    send "exit\r"
            }
        }

	catch close
	}
}

###### pdu reload
proc rPdu {iPdu iPort} {

     # reload
     if {$iPdu == "91" || $iPdu == "92" || $iPdu == "93" || $iPdu == "94" || $iPdu == "95" || $iPdu == "96"} {

       kickPduOut $iPdu
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
        kickPduOut 90
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

###### Kick pdu
proc kickPduOut {sPdu} {

    while 1 {
        spawn telnet 10.10.50.$sPdu
        expect {
            "Connection" {
                after 30000
                send "\r"
            }
            "Name" {
                send "apc\r"
                break
            }
        }
    }

    expect "Password"
    send "apc\r"
    expect "Control Console"
    send "4\r"
    expect "Connection Closed"

    catch close
    catch wait
}



###### Create port db
proc dbPort {sPort iPort sPro iPdu sPco} {

    upvar $iPort iPorts
    upvar $sPro sPros
    upvar $iPdu iPdus
    upvar $sPco sPcos

    kickPduOut 92
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
    regexp "(\[0-9]+)-\[ ]\\\[--]\[ ]+(\[0-9a-z]+)_[set sPort]_i(\[0-9]+)_\[0-9]-\[0-9]+_c(\[0-9]+)" $sDbPort sTmp iPorts sPros sIps sPcos
    if {[info exists iPorts] == 1} {
        set iPdus 92
        return
    }

    kickPduOut 95
    spawn telnet 10.10.50.95
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
    regexp "(\[0-9]+)-\[ ]+(\[0-9a-z]+)_[set sPort]_i(\[0-9]+)_\[0-9]-\[0-9]+_c(\[0-9]+)" $sDbPort sTmp iPorts sPros sIps sPcos
    if {[info exists iPorts] == 1} {
        set iPdus 95
        return
    }

    kickPduOut 90
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
	regexp "(\[0-9]+)-\[ ]\\\[--]\[ ]+(\[0-9a-z]+)_[set sPort]_i(\[0-9]+)_\[0-9]-\[0-9]+_c(\[0-9]+)" $sDbPort sTmp iPorts sPros sIps sPcos
	if {[info exists iPorts] == 1} {
		set iPdus 90 
		return 
	}

    
    kickPduOut 94
    spawn telnet 10.10.50.94
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
    regexp "(\[0-9]+)-\[ ]+(\[0-9a-z]+)_[set sPort]_i(\[0-9]+)_\[0-9]-\[0-9]+_c(\[0-9]+)" $sDbPort sTmp iPorts sPros sIps sPcos
    if {[info exists iPorts] == 1} {
        set iPdus 94
        return
    }


    kickPduOut 91
    spawn telnet 10.10.50.91

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
    regexp "(\[0-9]+)-\[ ]\\\[--]\[ ]+(\[0-9a-z]+)_[set sPort]_i(\[0-9]+)_\[0-9]-\[0-9]+_c(\[0-9]+)" $sDbPort sTmp iPorts sPros sIps sPcos
    if {[info exists iPorts] == 1} {
        set iPdus 91
        return
    }

    kickPduOut 93
    spawn telnet 10.10.50.93

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

    regexp "(\[0-9]+)-\[ ]\\\[--]\[ ]+(\[0-9a-z]+)_[set sPort]_i(\[0-9]+)_\[0-9]-\[0-9]+_c(\[0-9]+)" $sDbPort sTmp iPorts sPros sIps sPcos
    if {[info exists iPorts] == 1} {
        set iPdus 93
        return
    }

    kickPduOut 96
    spawn telnet 10.10.50.96
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
    regexp "(\[0-9]+)-\[ ]+(\[0-9a-z]+)_[set sPort]_i(\[0-9]+)_\[0-9]-\[0-9]+_c(\[0-9]+)" $sDbPort sTmp iPorts sPros sIps sPcos
    if {[info exists iPorts] == 1} {
        set iPdus 96
        return
    }

	return
}


######Update image for x86 via ONIE 
proc sUpdate_x86  {sPort sIp sIm sPro iPort iPdu sPco sApp}  {

       if {$sPco == "122"} {
           userKick $sPort       
       } else {
           userKickNew $sPort     
       }

	rPdu $iPdu $iPort
    	after 1000
      spawn telnet 10.10.50.$sPco 20$sPort
      set timeout -1 
      expect "PicOS"
      send "\x1b\[B"         
      expect "ONIE" 
      send "\r"
      expect "ONIE: Install OS" 
      send "\r"
      expect "ONIE: Starting ONIE Service Discovery"
      send  "\r"
      expect "ONIE:/ #"
      send "onie-nos-install tftp://$sIp/$sIm\r"
      
      while 1 {
          expect {
          "/yes:" {
              exp_send "yes\r"
              exp_continue
          }
          "System installs successfully" {
              exp_send "\r"
              break
          }
        }
      }   
   
      while 1 {
           expect {
               "XorPlus login:" {
                   send "admin\r"
               }
               "Password" {
                   send "pica8\r"
               }
               -ex "(current) UNIX password:" {
                   send "pica8\r"
               }
               -ex "Enter new UNIX password:" {
                   send "123456\r"
               }
               -ex "Retype new UNIX password: " {
                   send "123456\r"
               }
               "admin@" {
                   send "\r"
                   break
               }
           }
       }

       while 1 {
           expect {
               "admin@" {
                   send "sudo passwd root\r"
               }
               "Enter new UNIX password:" {
                   send "pica8\r"
               }
               "Retype new UNIX password: " {
                   send "pica8\r"
                   break
               }
           }
       }      
 
        while 1 {
            expect {
                "successfully" {
                    send "su\r"
                    break
                }
            }
        }
 
         while 1 {
             expect {
                 "Password:" {
                     send "pica8\r"
                     break
                 }
             }
         }
 
           while 1 {
               expect {
                   "root@" {
                       send "passwd admin\r"
                   }
                   "Enter new UNIX password:" {
                       send "pica8\r"
                   }
                   "Retype new UNIX password: " {
                       send "pica8\r"
                       break
                   }
               }
           }
           
            while 1 {
                expect {
                    "root@" {
                        send "picos_boot\r"
                        break
                    }
                }
            }

             ###Startup l2/l3 mode
		if {$sApp == 1} {
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
                        send "exit\r"
                        break
                    }
                }
            }           

           # Get the license type
           set cType ""
           while 1 {
               expect {
                   -ex "admin@" {
                        send "license -s\r"
                        expect -ex "license -s"
                        expect -re "(.*)admin@"
                        regexp "Type:\\s(\[0-9]+)GE" $expect_out(buffer) cTmp cType
                        send "\r"
                        break
                    }
                 }
             }

             if {$cType == 1} {
                 set licName "1GE-SITE-PICA8.lic"
             } elseif {$cType == 10} {
                 set licName "10GE-SITE-PICA8.lic"
             }

             # Get the license file and install
             if {$cType == 1 || $cType == 10} {
                foreach sName "$licName" dName "js.lic" {
                   while 1 {
                         expect {
                             -ex "admin@" {
                                 send "sudo scp build@10.10.50.16:/tftpboot/build/license/$sName /etc/picos/$dName\r"
                             }
                             -ex "input overrun" {
                                 send "\r"
                             }
                             -ex "yes/no" {
                                 send "yes\r"
                             }
                             -ex "y/n" {
                                 send "y\r"
                             }
                             -ex "assword" {
                                 send "build\r"
                                 break
                             }
                          }
                       }
                    }

                 while 1 {
                     expect {
                         -ex "admin@" {
                             send "sudo sync\r"
                             break
                          }
                      }
                  }

                 while 1 {
                      expect {
                         -ex "successfully" {
                              send "\r"
                              break
                         }
                         -ex "Install failed" {
                              send "\r"
                              break
                         }
                         -ex "admin@" {
                              send "sudo /usr/sbin/license -i /etc/picos/js.lic\r"
                         }
                         -ex "input overrun" {
                                send "\r"
                         }
                      }
                   }
               }

              while 1 {
                 expect {
                     -ex "admin@" {
                         send "sudo /etc/init.d/picos restart\r"
                         break
                      }
                  }
              }

              while 1 {
                  expect {
                     -ex "Starting: PicOS" {
                         send "\r"
                     }
                     -ex "admin@" {
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
                       -ex "admin@" {
                           send "cli\r"
                       }
                       -ex "XorPlus>" {
                           send "\r"
                           break
                       }
                   }
               }     

            } elseif {$sApp == 2}  {
                while 1 {
                    expect {
                        -ex "Enter your choice" {
                            send "2\r"
                            break
                        }
                    }
                }
    
                while 1 {
                    expect {
                        -ex "Configure the IP of management interface" {
                            send "1\r"
                        }
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
                        }
                        -ex "admin@" {
                            send "exit\r"
                            break
                        }
                    }
                }
    
                 while 1 {
                 	expect {
                     	"login:" {
                         	send "admin\r"
                     	}
                     	"Password:" {
                         	send "pica8\r"
                     	}
                         "admin@" {
                             send "\r"
                             break
                          }
                 	  }
                 }
    
                # Get the license type
                set cType ""
                while 1 {
                    expect {
                        -ex "admin@" {
                            send "license -s\r"
                            expect -ex "license -s"
                            expect -re "(.*)admin@"
                            regexp "Type:\\s(\[0-9]+)GE" $expect_out(buffer) cTmp cType
                            send "\r"
                            break
                        }
                    }
                }
                
                if {$cType == 1} {
                    set licName "1GE-SITE-PICA8.lic"
                } elseif {$cType == 10} {
                    set licName "10GE-SITE-PICA8.lic"
                }
                
                # Get the license file and install
                if {$cType == 1 || $cType == 10} {
                    foreach sName "$licName" dName "js.lic" {
                        while 1 {
                            expect {
                                -ex "admin@" {
                                    send "sudo scp build@10.10.50.16:/tftpboot/build/license/$sName /etc/picos/$dName\r"
                                }
                                -ex "input overrun" {
                                    send "\r"
                                }
                                -ex "yes/no" {
                                    send "yes\r"
                                }   
                                -ex "y/n" {
                                    send "y\r"
                                }
                                -ex "assword" {
                                    send "build\r"
                                    break
                                }
                            }
                        }
                    }
    
                    while 1 {
                        expect {
                            -ex "admin@" {
                                send "sudo sync\r"
                                break
                            }
                        }
                    }
                
                    while 1 {
                        expect {
                            -ex "successfully" {
                                send "\r"
                                break
                            }
                            -ex "Install failed" {
                                send "\r"
                                break
                            }
                            -ex "admin@" {
                                send "sudo /usr/sbin/license -i /etc/picos/js.lic\r"
                            }
                            -ex "input overrun" {
                                send "\r"
                            }
                        }
                    }
                }
    
                while 1 {
                    expect {
                        -ex "admin@" {
                            send "sudo /etc/init.d/picos restart\r"
                            break
                        }
                    }
                }
       
                while 1 {
                    expect {
                        -ex "Starting: PicOS" {
                            send "\r"
                            break
                        }
                    }
                }
            } else {
                while 1 {
                    expect {
                        -ex "Enter your choice" {
                            send "3\r"
                            break
                        }
                    }
                }
    
                while 1 {
                    expect {
                        -ex "root@" {
                            send "su admin\r"
                            break
                        }
                    }
                }
    
                # Get the license type
                set cType ""
                while 1 {
                    expect {
                        -ex "admin@" {
                            send "/usr/sbin/license -s\r"
                            expect -ex "license -s"
                            expect -re "(.*)admin@"
                            regexp "Type:\\s(\[0-9]+)GE" $expect_out(buffer) cTmp cType
                            send "\r"
                            break
                        }
                    }
                }
                
                if {$cType == 1} {
                    set licName "1GE-SITE-PICA8.lic"
                } elseif {$cType == 10} {
                    set licName "10GE-SITE-PICA8.lic"
                }
                
                # Get the license file and install
                if {$cType == 1 || $cType == 10} {
                    foreach sName "$licName" dName "js.lic" {
                        while 1 {
                            expect {
                                -ex "admin@" {
                                    send "sudo scp build@10.10.50.16:/tftpboot/build/license/$sName /etc/picos/$dName\r"
                                }
                                -ex "input overrun" {
                                    send "\r"
                                }
                                -ex "yes/no" {
                                    send "yes\r"
                                }
                                -ex "y/n" {
                                    send "y\r"
                                }
                                -ex "assword" {
                                    send "build\r"
                                    break
                                }
                            }
                        }
                    }
    
                    while 1 {
                        expect {
                            -ex "admin@" {
                                send "sudo sync\r"
                                break
                            }
                        }
                    }
                
                    while 1 {
                        expect {
                            -ex "successfully" {
                                send "\r"
                                break
                            }
                            -ex "Install failed" {
                                send "\r"
                                break
                            }
                            -ex "admin@" {
                                send "sudo /usr/sbin/license -i /etc/picos/js.lic\r"
                            }
                            -ex "input overrun" {
                                send "\r"
                            }
                        }
                    }
                }
    
                while 1 {
                    expect {
                        -ex "admin@" {
                            send "sudo /etc/init.d/picos restart\r"
                            break
                        }
                    }
                }
    
                while 1 {
                    expect {
                        -ex "options for PicOS" {
                            send "\r"
                            break
                        }
                    }
                }
    
                while 1 {
                    expect {
                        -ex "admin@" {
                            send "version\r"
                            break
                        }
                    }
                }
            }
}     
set sPort [lindex $argv 0]
set sIp [lindex $argv 1]
set sApp [lindex $argv 2]

if {$sPort == "" || $sIp == "" || $sApp == ""} {
    puts "\n===================Usage======================"
    puts "$argv0 sPort sIp sApp"
    puts "===================Usage======================"
    puts "1. sPort:    the console port of the box (eg. 01 means <10.10.50.122 2001>"
    puts "2. sIp:      ip address of server storing image:10.10.50.16"
    puts "3. sApp:     1 means <enter Xorplus>, 2 means <enter Ovs>, 3 means <Linux>"
    puts "\n===================Example===================="
    puts "$argv0 01 10.10.50.16  1"
    puts "===================Example===================="
    puts "1. sPort:       01"
    puts "2. sIp:         10.10.50.16"
    puts "3. sApp:         1"
} else {
	sCheck sVer
	###Get the platform,pdu and console port information
	dbPort $sPort iPort sPro iPdu sPco
	puts "********iPort is $iPort; sPro is $sPro; iPdu is $iPdu; sPco is $sPco********"
       if {[lsearch "2632 5712 2948 7032 671232" $sPro] == -1} {
           puts  "***$sPro is not X86 platform, so exits this update script***"
           exit   
       }
	set subject $sVer
	set result [regexp -linestop {\A[0-9]+\Z} $subject]
	if {$result == 1} {
	       GetInstallerImage  $sIp $sPro sIm $sVer
       } else {
		set sIp $sVer
	}

       sUpdate_x86  $sPort $sIp $sIm $sPro $iPort $iPdu $sPco $sApp
}

