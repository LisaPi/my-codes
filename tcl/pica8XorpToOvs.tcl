set aWs(sTitle) "Change platform from XorPlus to Ovs"
set aWs(sDescription) ""

proc pica8XorpToOvs {} {

    set timeout -1
    global aSetup
    global spawn_id
    global g_iResult

    set configurefile "pica"

    sdbPicaIxPortPairFmtGet PX1 XR1 PX2 XR2 PX3 XR3

    # Test start
    pica8TestStart

    # Get the Ip address 
    set sIp [pica8CheckCmd 1 "show interface management-ethernet"]
    regexp {Inet addr:\s+([0-9]+.[0-9]+.[0-9]+.[0-9]+)} $sIp sTmp sIp
   
    picaCliCmdRun "exit discard"
    picaCliCmdRun "exit"
    set sBranch [pica8OvsCmd 1 "version"]
    regexp "Linux System Version\/Revision : (\[0-9]+.\[0-9]+).*Linux" $sBranch tmp Branch

    if {$Branch == 1.1} {
       set configurefile "xorplus"
    }

    picaCliCmdRun "cli"
    picaCliCmdRun "configure"

    # Change platform from XorPlus to Ovs
    set spawn_id $aSetup(pica,1,sSpawnId) 
    send "\r"

    expect {
        "XorPlus#" {
            send "exit discard\r"; exp_continue
        }
        "XorPlus>" {
            send "syslog monitor off\r"
        }
    }


    expect {
        "XorPlus>" {
            send "exit\r"
        }
    }

    expect {
        "login" {
            send "root\r"; exp_continue
        }
        "assword:" {
            send "pica8\r"; exp_continue
        }
        -re "root@" {
            send "\r"
        }
        "XorPlus\\$" {
            send "\r"
        }
    }

    expect {
        "root@" {
            send "\r"
        }
        "successfully" {
            send "\r"
        }
        "XorPlus\\$" {
            send "sudo passwd root\r"; exp_continue
        }
        "Enter new UNIX password:" {
            send "pica8\r"; exp_continue
        }
        "Retype new UNIX password:" {
            send "pica8\r"; exp_continue
        }
    }

    expect {
        "root@" {
            send "picos_boot\r"
        }
        "assword" {
            send "pica8\r"; exp_continue
        }
        "XorPlus\\$" {
            send "su\r"; exp_continue
        }
    }

    expect {
        -ex "Enter your choice" {
            send "2\r"
        }
    }

    expect {
        "Configure the IP of management interface" {
            send "2\r"; exp_continue
        }
        "static IP and netmask for the switch" {
            send "$sIp/24\r"; exp_continue
        }
        "gateway IP" {
            send "[string range $sIp 0 7].1\r"; exp_continue
        }
        -re "root@" {
            send "\r"
        }
    }

    expect {
        "root@" {
            send "/$configurefile/bin/shell/telnet_root-login.sh allow\r"
        }
    }

    expect {
        "root@" {
            send "/$configurefile/bin/shell/telnet_disable.sh false\r"
        }
    }

    expect {
        -re "root@" {
            send "license -r\r"
        }
    }

    # Get the license type
    set cType ""
    expect {
        -ex "root@" {
            send "/usr/sbin/license -s\r"
            expect -ex "license -s"
            expect -re "(.*)root@"
            regexp "Type:\\s(\[0-9]+)GE" $expect_out(buffer) cTmp cType
            send "\r"
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
            expect {
                -ex "root@" {
                    send "scp build@10.10.50.16:/tftpboot/build/license/$sName /etc/picos/$dName\r"; exp_continue
                }
                -ex "input overrun" {
                    send "\r"; exp_continue
                }
                -ex "yes/no" {
                    send "yes\r"; exp_continue
                }
                -ex "y/n" {
                    send "y\r"; exp_continue
                }
                -ex "assword" {
                    send "build\r"
                }
            }
        }

        expect {
            -ex "root@" {
                send "sudo sync\r"
            }
        }

        expect {
            -ex "successfully" {
                send "\r"
            }
            -ex "Install failed" {
                send "\r"
            }
            -ex "root@" {
                send "/usr/sbin/license -i /etc/picos/js.lic\r"; exp_continue
            }
            -ex "input overrun" {
                send "\r"; exp_continue
            }
        }
    }

    expect {
        -ex "root@" {
            send "\r"
        }
    }

spawn telnet $sIp

    expect {
        -ex "XorPlus login:" {
            send "root\r"; exp_continue
        }
        -ex "assword" {
            send "pica8\r"; exp_continue
        }
        -ex "root@" {
            send "/etc/init.d/picos restart\r"
        }
    }

    expect {
        "root@XorPlus" {
            send "\r"
        }
    }

    expect {
        "root@" {
            send "/$configurefile/bin/shell/telnet_disable.sh false\r"
        }
    }

    expect {
        "root@" {
            send "/$configurefile/bin/shell/telnet_root-login.sh allow\r"
        }
    }

    expect {
        "root@" {
            send "su admin\r"
        }
    }

    expect {
        "admin@" {
            send "\r"
        }
    }

    pSleep 5
    set spawn_id $aSetup(pica,1,sSpawnId)
    send "\r"

    expect {
        "root@" {
            send "exit\r"
        }
    }

    expect {
        "admin@" {
            send "exit\r"
        }     
   }

    expect {
        "PicOS-OVS login:" {
            send "admin\r"; exp_continue
        }
        "assword:" {
            send "pica8\r"; exp_continue
        }
        "admin@" {
            send "\r"
        }
   }

    picaCliCmdRun "ovs-vsctl show"

	return
}
