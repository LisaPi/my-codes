#!/usr/bin/expect --

proc git_clone  {sIp sName sModel sBrs} {


    spawn ssh $sIp -l $sName
    while 1 {
        expect {
            "yes/no" {
                send "yes\r"
            }
            "password:" {
                send "$sName\r"
                break
            }
        }
    }
    expect "$sName@"
    set timeout -1
    send "cd /home/$sName/$sModel/release/pica8/branches \r"    
    while 1 {
         expect {
         "$sName@" {
             send "git clone http://code.pica8.local/repo/pica8.git\r"
         }
         "Username for" {
             send "build\r"
             expect -re "Password for"
             send "pica8build\r"  
             expect -re "$sName@"
             send "\r"
             break
         }             
       } 
     }
    
     while 1 {
        expect {
            "$sName@" {
                send "mv pica8 $sBrs\r"
                break
            }
        }
    }

     while 1 {
        expect {
            "$sName@" {
                send "cd /home/$sName/$sModel/release/pica8/branches/$sBrs\r"
                break
            }
        }
    }
    
     while 1 {
        expect {
            "$sName@" {
                send "git branch\r"
                break
            }
        }
    }

     while 1 {
        expect {
            "$sName@" {
                send "git checkout $sBrs\r"
                break
            }
        }
    }

     while 1 {
        expect {
            "$sName@" {
                send "git branch\r"
                break
            }
        }
    }
}

set sIp [lindex $argv 0]
set sName [lindex $argv 1]
set sModel [lindex $argv 2]
set sBrs [lindex $argv 3]

if {$sName == "" || $sIp == ""  || $sModel== "" || "sBrs"==""} {
    puts "\n===================Usage======================"
    puts "$argv0 sIp Username  sModel  branches"
    puts "===================Usage======================"
} else {
	set cUser [exec whoami]
	if {[string compare -nocase $sName $cUser] != 0} {
		puts "User:$cUser can not make the code of ower:$sName"
		exit
        }
        
    git_clone  $sIp  $sName  $sModel  $sBrs
}	