#!/usr/bin/env expect

# Kick pdu
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

# Check get new or specific image
proc sCheck {sVer} {

	upvar $sVer sVers

	set timeout 15
	send_user "Newest Image (input 0); specific image (input 1): specific directory (input 2):"
    expect_user {
    	-re "0\n" {set flag 0}
    	-re "1\n" {set flag 1}
        -re "2\n" {set flag 2}
    	timeout {set flag 0}
        -re "\n" {set flag 0}
	}

	if {$flag == 1} {
		set timeout 60

    	while 1 {
        	send_user "Version number: "
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

# get console server
proc sGetConsole {sConsole} {

	upvar $sConsole sConsoles

	set timeout 15
	send_user "select console server 10.10.50.123 (input 0); select console server 10.10.50.122 (input 1):"
    expect_user {
    	-re "0\n" {set flag 0}
    	-re "1\n" {set flag 1}
    	timeout {set flag 0}
        -re "\n" {set flag 0}
	}

	if {$flag == 0} {

		set sConsoles 123
		
	} else {

        set sConsoles 122
    }

	return
}


# Functon to do the send expect action
proc sExpect {exps cmds} {
    foreach exp $exps cmd $cmds {
	    while 1 {
            expect {
                "$exp" {
                    send "$cmd\r"
                    break
                }
            }
        }
    }
}

# pdu reload
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

# Get Image dirctory
proc sImage {sIp sPro sIm sRel {sVer 0}} {

    if {$sRel == 0} {
        set sDir daily
    } else {
        set sDir release
    }

    switch $sPro {
        "6700" {set sPro as6701_32x}
        "3924" {set sPro as5600_52x}
        "4654" {set sPro as4600_54t}
        "3296" {set sPro 3297}
    }

    upvar $sIm sIms

    set timetout 5
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
		send "ls -lt picos*\r"
		expect -re "(rw\[^\r]*)\r\n"
        regexp "(picos-\[-0-9.a-zA-Z]+-\[_0-9a-zA-Z]+(\[-a-zA-Z0-9.]+)?.tar.gz)" $expect_out(buffer) sTmp sIms
	} else {
		send "ls -lt picos*$sVer*\r"
		expect -re "(rw\[^\r]*)\r\n"
        regexp "(picos-\[-0-9.a-zA-Z]+-\[_0-9a-zA-Z]+(\[-a-zA-Z0-9.]+)?.tar.gz)" $expect_out(buffer) sTmp sIms
	}
    send "exit\r"
    expect "logout"

	catch close

    puts "sIms:$sIms"
}

# Create port db
proc dbPort {sConsole sPort iPort sPro iPdu} {

	upvar $iPort iPorts
       upvar $sPro sPros
	upvar $iPdu iPdus

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
	regexp "(\[0-9]+)-\[ ]\\\[--]\[ ]+(\[0-9a-z]+)_[set sPort]_i\[0-9]+_\[0-9]-\[0-9]+_c[set sConsole]\[ ]" $sDbPort sTmp iPorts sPros

	if {[info exists iPorts] == 1} {
		set iPdus 90 
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

    regexp "(\[0-9a-z]+)-\[ ]\\\[--]\[ ]+(\[0-9a-z]+)_[set sPort]_i\[0-9]+_\[0-9]-\[0-9]+_c[set sConsole]\[ ]" $sDbPort sTmp iPorts sPros
    if {[info exists iPorts] == 1} {
        set iPdus 91
        return
    }

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

    regexp "(\[0-9a-z]+)-\[ ]\\\[--]\[ ]+(\[0-9a-z]+)_[set sPort]_i\[0-9]+_\[0-9]-\[0-9]+_c[set sConsole]\[ ]" $sDbPort sTmp iPorts sPros
    if {[info exists iPorts] == 1} {
        set iPdus 92
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

    regexp "(\[0-9a-z]+)-\[ ]\\\[--]\[ ]+(\[0-9a-z]+)_[set sPort]_i\[0-9]+_\[0-9]-\[0-9]+_c[set sConsole]\[ ]" $sDbPort sTmp iPorts sPros
    if {[info exists iPorts] == 1} {
        set iPdus 93
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

    regexp "(\[0-9a-z]+)-\[ ]+(\[0-9a-z]+)_[set sPort]_i\[0-9]+_\[0-9]-\[0-9]+_c[set sConsole]\[ ]" $sDbPort sTmp iPorts sPros
    if {[info exists iPorts] == 1} {
        set iPdus 94
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

    regexp "(\[0-9a-z]+)-\[ ]+(\[0-9a-z]+)_[set sPort]_i\[0-9]+_\[0-9]-\[0-9]+_c[set sConsole]\[ ]" $sDbPort sTmp iPorts sPros
    if {[info exists iPorts] == 1} {
        set iPdus 95
        return
    }

    return

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

    regexp "(\[0-9a-z]+)-\[ ]+(\[0-9a-z]+)_[set sPort]_i\[0-9]+_\[0-9]-\[0-9]+_c[set sConsole]\[ ]" $sDbPort sTmp iPorts sPros
    if {[info exists iPorts] == 1} {
        set iPdus 96
        return
    }

    return
}

# Kill pdu
proc pduKill {iPdu} {
	foreach sIp {10.10.50.16 10.10.51.16} {
		spawn ssh root@$sIp

		while 1 {
			expect {
				"yes/no" {
					send "yes\r"
				}
            	"assword" {
                	send "pica8\r"
            	}
            	"root@" {
                	send "kill \$(ps aux|grep \"$iPdu\"|awk '{print \$2}')\r"
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
	}
}

# tftp copy
proc tftpCopy {sIp sName sDir} {

    spawn ssh $sIp -l $sName

    while 1 {
        expect {
            "yes/no" {
                send "yes\r"
                break
            }
            "assword" {
                send "$sName\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "$sName@" {
                send "rm /home/tftpboot/picos_ubi.img\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "$sName@" {
                send "cp /tftpboot/$sDir/picos_ubi.img /home/tftpboot\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "$sName@" {
                send "exit\r"
                break
            }
        }
    }

	catch close
}

# Kill user
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


# Kill user
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

# Function to update image
proc sUpdate {sPort sDir sIp sPro iPort iPdu sCon sApp sConsole} {

	# uboot cmd set
    set fCmd ""

	if {$sPro == 3290 || $sPro == 3295} {
        set fCmd {setenv bootargs root=/dev/ram console=ttyS0,$baudrate; bootm ffd00000 ff000000 ffee0000}
    } elseif {$sPro == 3780} {
        set fCmd {setenv bootargs root=/dev/ram console=ttyS0,$baudrate; bootm ffd00000 fef00000 ffee0000}
    } elseif {$sPro == 3920} {
        set fCmd {setenv bootargs root=/dev/ram mtdparts=physmap-flash.0:57728k(jffs2),3968k(ramdisk),3072k(kernel),128k(dtb),128k(u-boot-env),512k(u-boot) console=ttyS0,$baudrate; bootm EFC40000 EF860000 EFF40000}
    } elseif {$sPro == 3980} {
        set fCmd {setenv bootargs root=/dev/ram console=ttyS0,$baudrate; bootm ffd00000 fef00000 ffee0000}
    } elseif {$sPro == "3922"} {
        set fCmd {usb start;setenv bootargs root=/dev/ram rw console=$consoledev,$baudrate;ext2load usb 0:2 $ramdiskaddr $ramdiskfile;ext2load usb 0:2 $loadaddr $bootfile;ext2load usb 0:2 $fdtaddr $fdtfile;bootm $loadaddr  $ramdiskaddr $fdtaddr}
    } elseif {$sPro == "3930"} {
        set fCmd {setenv bootargs root=/dev/ram rw console=ttyS0,115200;usb start;ext2load usb 0:2 $loadaddr boot/uImage;ext2load usb 0:2 $fdtaddr boot/p2020rdb.dtb;ext2load usb 0:2 $ramdiskaddr boot/rootfs.ext2.gz.uboot;bootm $loadaddr $ramdiskaddr $fdtaddr}
    } elseif {$sPro == "3296"} {
        set fCmd {usb start;setenv bootargs root=/dev/ram rw console=ttyS0,115200;ext2load usb 0:2 $loadaddr boot/uImage;ext2load usb 0:2 $ramdiskaddr boot/$ramdiskfile;ext2load usb 0:2 $fdtaddr boot/$fdtfile;bootm $loadaddr $ramdiskaddr $fdtaddr}
    } elseif {$sPro == "3297"} {
        set fCmd {usb start;setenv bootargs root=/dev/ram rw console=ttyS0,115200;ext2load usb 0:2 $loadaddr boot/uImage;ext2load usb 0:2 $ramdiskaddr boot/$ramdiskfile;ext2load usb 0:2 $fdtaddr boot/$fdtfile;bootm $loadaddr $ramdiskaddr $fdtaddr}
    } elseif {$sPro == "3924" || $sPro == "5401"} {
        set fCmd ""
    } elseif {$sPro == "5101"} {
        set fCmd {mmc rescan;setenv bootarg root=/dev/ram rw console=$consoledev,$baudrate;ext2load mmc 0:2 $loadaddr $bootfile;ext2load mmc 0:2 $fdtaddr $fdtfile;ext2load mmc 0:2 $ramdiskaddr $ramdiskfile;bootm $loadaddr $ramdiskaddr $fdtaddr}
    }

    set 3290 {setenv bootargs root=/dev/hda1 rw noinitrd console=ttyS0,$baudrate; ext2load ide 0:1 0x1000000 boot/uImage;ext2load ide 0:1 0x400000 boot/LB9A.dtb;bootm 1000000 - 400000}
    set 3780 {setenv bootargs root=/dev/hda1 rw noinitrd console=ttyS0,$baudrate; ext2load ide 0:1 0x1000000 boot/uImage;ext2load ide 0:1 0x400000 boot/LB8.dtb;bootm 1000000 - 400000}
    set 3295 {setenv bootargs root=/dev/hda1 rw noinitrd console=ttyS0,$baudrate; ext2load ide 0:1 0x1000000 boot/uImage;ext2load ide 0:1 0x400000 boot/LB9.dtb;bootm 1000000 - 400000}
    set 3920 {mmcinfo;setenv bootargs root=/dev/mmcblk0p1 rw noinitrd console=ttyS0,115200 rootdelay=10;ext2load mmc 0:1 $loadaddr boot/uImage;ext2load mmc 0:1 $fdtaddr boot/LY2.dtb;bootm $loadaddr - $fdtaddr}
    set 3980 {setenv bootargs root=/dev/hda1 rw noinitrd console=ttyS0,$baudrate; ext2load ide 0:1 0x1000000 boot/uImage;ext2load ide 0:1 0x400000 boot/LB8D.dtb;bootm 1000000 - 400000}
    set 3922 {usb start;setenv bootargs root=/dev/sda1 rw noinitrd console=$consoledev,$baudrate rootdelay=10 $othbootargs;ext2load usb 0:1 $loadaddr boot/uImage ;ext2load usb 0:1 $fdtaddr boot/p2020rdb.dtb;bootm $loadaddr - $fdtaddr}
    set 3930 {usb start;setenv bootargs root=/dev/sda1 rw noinitrd console=$consoledev,$baudrate rootdelay=10;ext2load usb 0:1 $loadaddr boot/uImage;ext2load usb 0:1 $fdtaddr boot/p2020rdb.dtb;bootm $loadaddr - $fdtaddr}
	set 3296 {usb start;setenv bootargs root=/dev/sda1 rw noinitrd console=$consoledev,$baudrate rootdelay=10;ext2load usb 0:1 $loadaddr boot/$bootfile;ext2load usb 0:1 $fdtaddr boot/$fdtfile;bootm $loadaddr - $fdtaddr}
	set 3297 {usb start;setenv bootargs root=/dev/sda1 rw noinitrd console=$consoledev,$baudrate rootdelay=10;ext2load usb 0:1 $loadaddr boot/$bootfile;ext2load usb 0:1 $fdtaddr boot/$fdtfile;bootm $loadaddr - $fdtaddr}
    set 5401 {setenv bootargs root=/dev/mmcblk0p1 rw rootdelay=10 console=$consoledev,$baudrate;mmc rescan;ext2load mmc 0:1 $loadaddr boot/uImage;ext2load mmc 0:1 $fdtaddr boot/p2020.dtb;bootm $loadaddr - $fdtaddr}
    set 5101 {mmc rescan;setenv bootargs root=/dev/mmcblk0p1 rw console=$consoledev,$baudrate rootdelay=10;ext2load mmc 0:1 $loadaddr boot/uImage;ext2load mmc 0:1 $fdtaddr boot/p2020.dtb;bootm $loadaddr - $fdtaddr}
    set 3924 {usb start;setenv bootargs root=/dev/sda1 rw noinitrd console=$consoledev,$baudrate rootdelay=10;ext2load usb 0:1 $loadaddr boot/uImage;ext2load usb 0:1 $fdtaddr boot/p2020rdb.dtb;bootm $loadaddr - $fdtaddr}
    set 6700 {setenv bootargs root=/dev/sda1 rw console=$consoledev,$baudrate rootdelay=10;usb start;ext2load usb 0:1 $loadaddr boot/uImage;ext2load usb 0:1 $fdtaddr boot/p2020rdb.dtb;bootm $loadaddr - $fdtaddr}

    set framboot ""

    if {$sPro == 3922} {
        set framboot {setenv bootargs root=/dev/ram rw console=$consoledev,$baudrate $othbootargs; tftp $ramdiskaddr $base/3922/rootfs.ext2.gz.uboot;tftp $loadaddr $base/3922/uImage;tftp $fdtaddr $base/3922/p2020rdb.dtb;bootm $loadaddr $ramdiskaddr $fdtaddr}
    }

    if {$sPro == 3296 || $sPro == 3297} {
        set framboot {setenv bootargs root=/dev/ram rw console=ttyS0,115200;tftp $ramdiskaddr $base/3296/rootfs.ext2.gz.uboot;;tftp $loadaddr $base/3296/uImage;tftp $fdtaddr $base/3296/p2020rdb.dtb;bootm $loadaddr $ramdiskaddr $fdtaddr}
    }

    if {$sPro == 5401} {
        set framboot {setenv bootargs root=/dev/ram rw console=$consoledev,$baudrate $othbootargs; tftp $ramdiskaddr $base/5401/rootfs.ext2.gz.uboot;tftp $loadaddr $base/5401/uImage;tftp $fdtaddr $base/5401/p2020.dtb;bootm $loadaddr $ramdiskaddr $fdtaddr}
    }

    if {$sPro == 3924} {
        set framboot {setenv bootargs root=/dev/ram rw console=$consoledev,$baudrate;tftp $loadaddr $base/3924/uImage;tftp $fdtaddr $base/3924/p2020rdb.dtb;tftp $ramdiskaddr $base/3924/rootfs.ext2.gz.uboot;bootm $loadaddr $ramdiskaddr $fdtaddr}
    }

    if {$sPro == 5101} {
        set framboot {setenv bootargs root=/dev/ram rw console=$consoledev,$baudrate $othbootargs; tftp $ramdiskaddr $base/5101/rootfs.ext2.gz.uboot;tftp $loadaddr $base/5101/uImage;tftp $fdtaddr $base/5101/p2020.dtb;bootm $loadaddr $ramdiskaddr $fdtaddr}
    }

    if {$sPro == 6700} {
        set framboot {setenv bootargs root=/dev/ram rw console=$consoledev,$baudrate;tftp $loadaddr $base/6700/uImage;tftp $fdtaddr $base/6700/p2020rdb.dtb;tftp $ramdiskaddr $base/6700/rootfs.ext2.gz.uboot;bootm $loadaddr $ramdiskaddr $fdtaddr}
    }

    if {$sPro == 3290} {
        set bCmd u3290
    } elseif {$sPro == 3780} {
        set bCmd u3780
    } elseif {$sPro == 3295} {
        set bCmd u3295
    } elseif {$sPro == 3920} {
        set bCmd u3920
    } elseif {$sPro == 3980} {
        set bCmd u3980
    } elseif {$sPro == "3922"} {
        set bCmd u3922
    } elseif {$sPro == "3930"} {
        set bCmd u3930
    } elseif {$sPro == "3296"} {
        set bCmd u3296
    } elseif {$sPro == "6700"} {
        set bCmd u6700
    }


    if {$sConsole == 123} {
	userKickNew $sPort
   } else {
       userKick $sPort
   }
   
	rPdu $iPdu $iPort
    	after 2000

    	spawn telnet 10.10.50.$sConsole 20$sPort

    	while 1 {
        	expect {
            	"Starting Power-On Self Test" {
                	send "\003"
            	}
            	"DRAM Test" {
                	send "\025"
            	}
            	"assword" {
                	send "mercury\r"
            	}
            	"stop autoboot" {
                	send "\003\r"
            	}
            	-re "=>|Urus-II>|Urus2>|Cabrera2>" {
                	send "\r"
                	break
            	}
        	}
    	}

        while 1 {
            expect {
                -re "=>|Urus-II>|Urus2>|Cabrera2>" {
                    send "setenv base build/uboot\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                -re "=>|Urus-II>|Urus2>|Cabrera2>" {
                    send "setenv ipaddr 10.10.51.76\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                -re "=>|Urus-II>|Urus2>|Cabrera2>" {
                    send "setenv serverip 10.10.50.16\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                -re "=>|Urus-II>|Urus2>|Cabrera2>" {
                    send "setenv gatewayip 10.10.51.1\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                -re "=>|Urus-II>|Urus2>|Cabrera2>" {
                    send "setenv netmask 255.255.255.0\r"
                    break
                }
            }
        }

        if {$sPro == "3922" || $sPro == "3924"} {

            foreach iHead {consoledev loadaddr fdtaddr ramdiskaddr} iValue {ttyS0 0x2000000 0xE000000 0x3000000} {
                while 1 {
                    expect {
                        -re "=>|Urus-II>|Urus2>|Cabrera2>" {
                            send "setenv $iHead $iValue\r"
                            break
                        }
                    }
                }
            }
        }

		while 1 {
			expect {
				-re "=>|Urus-II>|Urus2>|Cabrera2>" {
					send "setenv fCmd \'$fCmd\'\r"
					break
				}
			}
		}

        while 1 {
            expect {
                -re "=>|Urus-II>|Urus2>|Cabrera2>" {
                    send "setenv framboot \'$framboot\'\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                -re "=>|Urus-II>|Urus2>|Cabrera2>" {
                    send "setenv picos \'[set [set sPro]]\'\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                -re "=>|Urus-II>|Urus2>|Cabrera2>" {
                    send "setenv bootcmd 'run picos'\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                -re "=>|Urus-II>|Urus2>|Cabrera2>" {
                    send "saveenv\r"
                }
                "done" {
                    send "\r"
                    break
                }
            }
        }

        if {$sPro == "3922" || $sPro == "3296" || $sPro == "3297" || $sPro == "3924" || $sPro == "5401" || $sPro == "5101" || $sPro == "6700"} {
            while 1 {
                expect {
                    -re "=>|Urus-II>|Urus2>|Cabrera2>" {
                        send "run framboot\r"
                        break
                    }
                }
            }
        } else {
            while 1 {
                expect {
                    -re "=>|Urus-II>|Urus2>|Cabrera2>" {
                        send "run fCmd\r"
                        break
                    }
                }
            }
        }

		if {$sPro == "3290" || $sPro == "3295" || $sPro == "3780"} {
            while 1 {
                expect {
                    "Topology is found" {
                        send "\r"
                        break
                    }
                }
            }

        	while 1 {
            	expect {
                	"Enter your choice" {
                    	send "\004\r"
                	}
                	"BCM" {
                    	send "\004\r"
                	}
                	"#" {
                    	send "\r"
						break
                	}
            	}
        	}
		} elseif {$sPro == "3920"} {
            while 1 {
                expect {
                    "Enter your choice" {
                        send "3\r"
						break
                    }
                }
            }

            while 1 {
                expect {
                    "System Shell" {
                        send "7\r"
                        break
                    }
                }
            }

        	while 1 {
            	expect {
                	"login:" {
                    	send "root\r"
                	}
                	"Password" {
                    	send "root123\r"
                	}
                	"#" {
                    	send "\r"
                    	break
                	}
            	}
        	}
		} elseif {$sPro == "3922" || $sPro == "3924" || $sPro == "6700"} {
        	while 1 {
            	expect {
                	"Attached SCSI disk" {
                    	send "\r"
                    	break
                	}
            	}
        	}

            while 1 {
                expect {
                    "#" {
                        send "\r"
                        break
                    }
                }
            }
		} elseif {$sPro == "3930"} {
            while 1 {
                expect {
                    "Attached SCSI removable disk" {
                        send "\r"
                        break
                    }
                }
            }

            while 1 {
                expect {
                    "#" {
                        send "\r"
                        break
                    }
                }
            }
        } elseif {$sPro == "3296" || $sPro == "3297"} {
            while 1 {
                expect {
                    "Attached SCSI removable disk" {
                        send "\r"
                        break
                    }
                }
            }

            while 1 {
                expect {
                    "#" {
                        send "\r"
                        break
                    }
                }
            }
        } elseif {$sPro == "5401" || $sPro == "5101"} {
            while 1 {
                expect {
                    "mmcblk0: mmc0" {
                        send "\r"
                        break
                    }
                }
            }

            while 1 {
                expect {
                    "#" {
                        send "\r"
                        break
                    }
                }
            }
        }

		if {$sPro == "3920" || $sPro == "5401" || $sPro == "5101"} {
            while 1 {
                expect {
                    "#" {
                        send "mount /dev/mmcblk0p1 /mnt/sd_card\r"
                        break
                    }
                }
            }

            while 1 {
                expect {
                    "#" {
                        send "cd /mnt/sd_card\r"
                        break
                    }
                }
            }
		} elseif {$sPro == "3922" || $sPro == "3930" || $sPro == "3296" || $sPro == "3297" || $sPro == "3924" || $sPro == "6700"} {
            while 1 {
                expect {
                    "#" {
                        send "mount /dev/sda1 /mnt\r"
                        break
                    }
                }
            }

            while 1 {
                expect {
                    "#" {
                        send "cd /mnt\r"
                        break
                    }
                }
            }
		} else {
            while 1 {
                expect {
                    "#" {
                        send "mount /dev/hda1  /cf_card\r"
                        break
                    }
                }
            }

            while 1 {
                expect {
                    "#" {
                        send "cd  /cf_card\r"
                        break
                    }
                }
            }
		}

		if {$sCon == 0} {

            while 1 {
                expect {
                    "#" {
                        send "rm -rf *\r"
                        break
                    }
                }
            }
		} else {
			while 1 {
        		expect {
   	         		"#" {
                		send "pwd\r"
                		expect -ex "pwd"
                		expect -re "(.*)#"
                		regexp "(\[-/0-9a-zA-Z_]+)" $expect_out(buffer) sTmp sPwd
                		send "\r"
                		break
            		}
        		}
    		}

            while 1 {
                expect {
                    "#" {
                        send "rm *\r"
                        break
                    }
                }
            }

            while 1 {
                expect {
                    "#" {
                        send "ls | grep -v pica | xargs rm -rf\r"
                        break
                    }
                }
            }

            while 1 {
                expect {
                    "#" {
                        send "cd pica\r"
                        break
                    }
                }
            }

            while 1 {
                expect {
                    "#" {
                        send "ls | grep -v config | xargs rm -rf\r"
                        break
                    }
                }
            }

            while 1 {
                expect {
                    "#" {
                        send "cd config\r"
                        break
                    }
                }
            }

            while 1 {
                expect {
                    "#" {
                        send "ls | grep -v pica_startup.boot | xargs rm -rf\r"
                        break
                    }
                }
            }

            while 1 {
                expect {
                    "#" {
                        send "cd $sPwd\r"
                        break
                    }
                }
            }
		}

		while 1 {
			expect {
				"#" {
					send "udhcpc\r"
					break
				}
			}
		}

        while 1 {
            expect {
                "#" {
                    send "ping $sIp\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "bytes from" {
                    send "\003\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "#" {
                    send "ifconfig\r"
                    expect -ex "ifconfig"
                    expect -re "(.*)#"
                    regexp "inet addr:(\[0-9]+.\[0-9]+.\[0-9]+.\[0-9]+)" $expect_out(buffer) oTmp oIp
                    send "\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "#" {
                    send "tftp -g -r $sDir -l rootfs.tar.gz  $sIp\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "#" {
                    send "sync\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "#" {
                    send "tar -zxvf rootfs.tar.gz\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "#" {
                    send "sync\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "#" {
                    send "reboot\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "The system is going down NOW" {
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
                    send "root\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "assword" {
                    send "pica8\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "Login incorrect" {
                    send "\r"
                    set lFlag 0
                    break
                }
                "root@" {
                    send "\r"
                    set lFlag 1
                    break
                }
            }
        }

        if {$lFlag == 0} {
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

        }

        while 1 {
            expect {
                "root@" {
                    send "picos_boot\r"
                    break
                }
            }
        }

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

            if {$lFlag == 0} {

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
            } else {

                while 1 {
                    expect {
                        "XorPlus login:" {
                            send "admin\r"
                        }
                        "Password:" {
                            send "pica8\r"
                        }
                        "XorPlus>" {
                            send "\r"
                            break
                        }
                    }
                }
            }
		} elseif {$sApp == 2} {
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
                    -ex "Please set a static IP and netmask for the switch" {
                        send "$oIp/24\r"
                    }
                    -ex "Please set the gateway IP" {
                        send "[string range $oIp 0 7].1\r"
                    }
                    -ex "root@" {
                        send "/etc/init.d/picos restart\r"
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
                    -ex "lighttpd" {
                        send "\r"
                        break
                    }
                }
            }

            while 1 {
                expect {
                    -ex "admin@" {
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
                        send "\r"
                        break
                    }
                }
            }
        }
  }

set sPort [lindex $argv 0]
set sIp [lindex $argv 1]
set sCon [lindex $argv 2]
set sRel [lindex $argv 3]
set sApp [lindex $argv 4]

if {$sPort == "" || $sIp == "" || $sCon == "" || $sApp == "" || $sRel == ""} {
    puts "\n===================Usage======================"
    puts "$argv0 sPort sIp sCon sRel"
    puts "===================Usage======================"
    puts "1. sPort:    the console port of the box (eg. 01 means 2001)"
    puts "2. sIp:      ip address of server storing image"
    puts "3. sCon:     0 means <delete all files, include pica_startup.boot>, 1 means <delete all files, exclude pica_startup.boot>"
    puts "4. sRel:     0 means <daily version>"
    puts "5. sApp:     1 means <enter Xorplus>, 2 means <enter Ovs>, 3 means <None>"
    puts "\n===================Example===================="
    puts "$argv0 01 10.10.50.16 0 0 1"
    puts "===================Example===================="
    puts "1. sPort:       01"
    puts "2. sIp:         10.10.50.16"
    puts "3. sCon:         0"
    puts "4. sRel:         0"
    puts "5. sApp:         1"
} else {
	sCheck sVer
	sGetConsole sConsole
	dbPort $sConsole $sPort iPort sPro iPdu

	set subject $sVer
	set result [regexp -linestop {\A[0-9]+\Z} $subject]
	if {$result == 1} {
		sImage $sIp $sPro sIm $sRel $sVer
        if {$sRel == 0} {

            if {$sPro == 6700} {
                set sDir "build/daily/as6701_32x/$sIm"
            } elseif {$sPro == 3924} {
                set sDir "build/daily/as5600_52x/$sIm"
            } elseif {$sPro == 4654} {
                set sDir "build/daily/as4600_54t/$sIm"
            }  elseif {$sPro == 3296}  {
                set sDir "build/daily/3297/$sIm"
            } else {
		        set sDir "build/daily/$sPro/$sIm"
            }
        } else {
            set sDir "build/release/$sPro/$sIm"
        }
	} else {
		set sDir $sVer
	}

	sUpdate $sPort $sDir $sIp $sPro $iPort $iPdu $sCon $sApp $sConsole
}
