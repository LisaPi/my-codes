#!/usr/bin/env expect 

log_user 1

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

# Get user name by ip
proc ipUser {iServers iIp} {

    foreach iServer $iServers {
        spawn ssh $iServer -l build
        while 1 {
            expect {
                "yes/no" {
                    send "yes\r";
                }
                "password:" {
                    send "build\r"
                }
                "build@" {
                    send "\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "build@" {
                    send "last -x | grep $iIp\r"
                    expect -ex "last -x | grep $iIp"
                    expect -re "(.*)build@"
                    regexp "(\[a-zA-Z.]+).*?$iIp" $expect_out(buffer) iTmp iUse
                    send "exit\r"
                    break
                }
            }
        }

        if {[info exists iUse] == 1} {
            puts "iUse:$iUse"
            return $iUse
        }
    }

    if {[info exists iUse] == 0} {
        puts "iIp:$iIp"
        return $iIp
    }

    catch close 
    catch wait
}

# Single box user
proc sboxUser {sIp sPort sUser} {

    upvar $sUser sUse

    set timeout 5
    if {[string length $sPort ] == 1} {
        set sPort 0$sPort
    }

    userServer $sIp sFlag

    if {$sIp == "10.10.53.51"} {
        set cUser "root"
        set cPwd "pica8"
    } else {
        set cUser "build"
        set cPwd "build"
    }

    if {$sFlag == 1} {
        spawn ssh $sIp -l $cUser
        while 1 {
            expect {
                "yes/no" {
                    send "yes\r";
                }
                "password:" {
                    send "$cPwd\r"
                }
                "$cUser@" {
                    send "\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "$cUser@" {
                    send "ps axo user:24,cmd | grep \"telnet 10.10.50.123 20$sPort\" | grep -v grep |  awk '{print \$1}'\r"
                    expect -ex {print}
                    expect -re "(.*)$cUser@"
                    regexp "(\[a-z]+)" $expect_out(buffer) sTmp sUse
                    send "exit\r"
                    break
                }
            }
        }

        catch close
        catch wait

    } else {
        set sUse $sIp
    }
}

# Single box server
proc sboxServer {sPort sIp} {

    if {[string index $sPort 0] == 0} {
        set sPort [string trimleft $sPort "0"]
    }

    upvar $sIp sIps

    spawn telnet 10.10.50.122
    expect {
        "Username>" {send "su\r"; exp_continue}
        "Local_" {send "su override\r"; exp_continue}
        "Password>" {send "system\r"}
    }

    while 1 {
        expect {
            "Local_" {
                send "show que\r"
                expect -ex {show que}
                expect -re {Local_}
                regexp "(\[0-9]+.\[0-9]+.\[0-9]+.\[0-9]+)\[ ]+\\(none\\)\[ ]+Port_$sPort "  $expect_out(buffer) sTmp sIps
                send "\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "Local_" {
                send "logout\r"
                break
            }
        }
    }

    catch close
    catch wait

    if {![info exists sIps]} {
        if {[string length $sPort] == 1} {
            set sPort 0$sPort
        }

        puts "\n######################"
        puts "20$sPort is not used!"
        puts "######################"
        exit
    }

}

# Get the server or user ip 
proc boxServer {sSerPort} {

    upvar $sSerPort sSerPorts

	spawn telnet 10.10.50.122
	expect {
		"Username>" {send "su\r"; exp_continue}
		"Local_" {send "su override\r"; exp_continue}
		"Password>" {send "system\r"}
	}

    while 1 {
		expect {
        	"Local_" {
            	send "show que\r"
				expect -ex {show que}
				expect -re {Local_}
                set sSerPorts $expect_out(buffer)
				send "\r"
            	break
        	}
		}
    }

    while 1 {
        expect {
            "Local_" {
                send "logout\r"
                break
            }
        }
    }

    catch close
    catch wait
}

# Get the server or user ip using ssh 
proc boxServerSSH {sSerPort} {

    set timeout -1

    upvar $sSerPort sSerPorts

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
                send "list\r"
                expect -ex "list\r"
                expect -re "(.*)sessions>"
                set sSerPorts $expect_out(buffer)
                send "\r"
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

# Check the ip is user or server
proc userServer {sIp sFlag} {

    set time 60
    upvar $sFlag sFlags

    if {$sIp == "10.10.53.51"} {
        set sUser "root"
        set sPwd "pica8"
    } else {
        set sUser "build"
        set sPwd "build"
    }

    spawn ssh $sIp -l $sUser
    while 1 {
        expect {
            "Connection refused" {
                set sFlags 0
                return
            }
            "Permission" {
                set sFlags 0
                return
            }
            "yes/no" {
                send "yes\r"
            }
            "assword" {
                send "$sPwd\r"
            }
            "$sUser@" {
                set sFlags 1
                return
            }
            timeout {
                set sFlags 0
                return
            }
        }
    }

    catch close
    catch wait
}

# Get the user name or ip
proc boxUser {sIp sUser} {

    upvar $sUser uUser
	set timeout -1


    if {$sIp == "10.10.53.51"} {
        set cUser "root"
        set cPwd "pica8"
    } else {
        set cUser "build"
        set cPwd "build"
    }

    spawn ssh $sIp -l $cUser
	while 1 {
		expect {
			"yes/no" {
				send "yes\r"; 
			}
			"password:" {
				send "$cPwd\r"
			}
            "$cUser@" {
                send "\r"
			    break
            }
	    }
    }

	while 1 {
        expect {
            "$cUser@" {
				send "ps axo user:24,cmd | grep telnet | grep -v grep\r"
				expect -ex {ps axo}
				expect -re "(.*)$cUser@"
                set uUser $expect_out(buffer)  				
                send "exit\r"
                break
            }
        }
    }

    catch close
    catch wait

    return 
}

# Create port db
proc boxPortPro {sCaps} {

    upvar $sCaps uCaps

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

	catch close
    catch wait

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
                set sDbPort1 $expect_out(buffer)
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

    catch close
    catch wait

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
                set sDbPort2 $expect_out(buffer)
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

    catch close
    catch wait

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
                set sDbPort3 $expect_out(buffer)
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

    catch close
    catch wait

    set uCaps "$sDbPort $sDbPort1 $sDbPort2 $sDbPort3"

	return
}

proc sBoxOwner {subject sPort sDir} {

    # Do for console port: 123
    set pos 0
    while {[regexp -indices -start $pos -linestop -nocase {([0-9]{4})_([0-9]{2})_i[0-9]{3}_c123} $subject offsets]==1} {
        set pos [expr {1+[lindex $offsets 1]}]
        lappend result [string range $subject [lindex $offsets 0] [lindex $offsets 1]]
    }
    set sProPortIps $result
    set result $sProPortIps
    foreach iResult $result {
        regexp "(\[0-9]{4})_(\[0-9]{2})_i(\[0-9]{3})" $iResult iTmp iPro iPort iIp
        lappend iPros $iPro
        lappend iPorts $iPort
        lappend iIps $iIp
    }

    set tPort $sPort

    if {1} {
        # Bakup up type
        set pType $sPort

        # Get server ip, console port from <show que>
        boxServerSSH sSerPorts

        set result ""
        set subject $sSerPorts
        set pos 0
        while {[regexp -indices -start $pos -linestop -nocase "ttyS(\[0-9]+)\\s+(\[0-9]+.\[0-9]+.\[0-9]+.\[0-9]+):" $subject offsets]==1} {
            set pos [expr {1+[lindex $offsets 1]}]
            lappend result [string range $subject [lindex $offsets 0] [lindex $offsets 1]]
        }
        set qSerPort $result

        set result $qSerPort
        foreach iResult $result {
            regexp "ttyS(\[0-9]+)\\s+(\[0-9]+.\[0-9]+.\[0-9]+.\[0-9]+):" $iResult iTmp iPort iServer
            lappend qServers $iServer
  
            if {[string length $iPort] == 1} {

                set iPort 0$iPort
            }
            lappend qPorts $iPort
        }

        set nServers ""
        set qFlags ""
        foreach qServer $qServers {
            if {[lsearch $nServers $qServer] == -1} {
                userServer $qServer sFlag
                if {$sFlag == 1} {
                    lappend nServers $qServer
                }
            }
        }

        set tServers ""
        foreach nServer $nServers {
            boxUser $nServer sUser
            lappend tServers $sUser
        }

        set result ""
        foreach tServer $tServers {
            set subject $tServer
            set pos 0
            while {[regexp -indices -start $pos -linestop -nocase {([a-z.]+)[ ]+[0-9/a-zA-Z+:. ]+telnet[ ]+10.10.50.123+[ ]+20([0-9]+)} $subject offsets]==1} {
                set pos [expr {1+[lindex $offsets 1]}]
                lappend result [string range $subject [lindex $offsets 0] [lindex $offsets 1]]
            }
        }
        foreach iResult $result {
            regexp {([a-z.]+)[ ]+[0-9/a-zA-Z+:. ]+telnet[ ]+[0-9.]+[ ]+20([0-9]+)} $iResult iTmp iUser iPort
            lappend bUsers $iUser
            lappend bPorts $iPort
        }

        set iUsers ""
        foreach iPort $iPorts {
            set sIndex [lsearch $bPorts $iPort]
            if {$sIndex != -1} {
                lappend iUsers [lindex $bUsers $sIndex]
            } else {
                set sIndex1 [lsearch $qPorts $iPort]
                if {$sIndex1 != -1} {
                    lappend iUsers [lindex $qServers $sIndex1]
                } else {
                    lappend iUsers "None"
                }
            }
        }

        set fobj [open $sDir/console.txt w]
        foreach iPort $iPorts {
            puts $fobj "123_$iPort"
        }
        close $fobj

        set sHead [open $sDir/boxOwner.html w]
        puts $sHead ""
        puts $sHead "<table width=\"70%\" border=\"1\" cellspacing=\"1\"\
                       cellpadding=\"1\">"
        puts $sHead "<tr>"
        puts $sHead "<th align=\"centre\">UserName</th>"
        puts $sHead "<th align=\"centre\">ConsolePort</th>"
        puts $sHead "<th align=\"centre\">ConsoleIp</th>"
        puts $sHead "<th align=\"centre\">ModelType</th>"
        puts $sHead "</tr>"

        puts ""
        puts [format "%-15s%-15s%-15s%-15s" "User" "ConsolePort" "ConsoleIp" "Model"]
        foreach iUser $iUsers iPort $iPorts iIp $iIps iPro $iPros {

            if {[regexp "\[0-9]{4}" $tPort] == 1} {
                if {[string compare [string range $tPort 0 1] "20"] == 0} {
                    if {[string compare $tPort 20$iPort] == 0} {
                        puts [format "%-15s%-15s%-15s%-15s"  $iUser 123_20$iPort 10.10.51.$iIp $iPro]
  
                        puts $sHead "<tr>"
                        puts $sHead "<td align=\"left\"> $iUser </td>"
                        puts $sHead "<td align=\"left\"> 123_20$iPort</td>"
                        puts $sHead "<td align=\"left\"> 10.10.50.$iIp </td>"
                        puts $sHead "<td align=\"left\"> $iPro </td>"
                        puts $sHead "</tr>"

                    }
                } else {
                    if {$pType == $iPro} {
                        puts [format "%-15s%-15s%-15s%-15s"  $iUser 123_20$iPort 10.10.51.$iIp $iPro]

                        puts $sHead "<tr>"
                        puts $sHead "<td align=\"left\"> $iUser </td>"
                        puts $sHead "<td align=\"left\"> 123_20$iPort</td>"
                        puts $sHead "<td align=\"left\"> 10.10.50.$iIp </td>"
                        puts $sHead "<td align=\"left\"> $iPro </td>"
                        puts $sHead "</tr>"
                    }
                }
            } elseif {[string length $tPort] == 2} {
                if {[string compare $tPort $iPort] == 0} {
                    puts [format "%-15s%-15s%-15s%-15s"  $iUser 123_20$iPort 10.10.51.$iIp $iPro]

                    puts $sHead "<tr>"
                    puts $sHead "<td align=\"left\"> $iUser </td>"
                    puts $sHead "<td align=\"left\"> 123_20$iPort</td>"
                    puts $sHead "<td align=\"left\"> 10.10.50.$iIp </td>"
                    puts $sHead "<td align=\"left\"> $iPro </td>"
                    puts $sHead "</tr>"
                }
            } else {
               puts [format "%-15s%-15s%-15s%-15s"  $iUser 123_20$iPort 10.10.51.$iIp $iPro]

               puts $sHead "<tr>"
               puts $sHead "<td align=\"left\"> $iUser </td>"
               puts $sHead "<td align=\"left\"> 123_20$iPort</td>"
               puts $sHead "<td align=\"left\"> 10.10.50.$iIp </td>"
               puts $sHead "<td align=\"left\"> $iPro </td>"
               puts $sHead "</tr>"
            }
        }

        #puts $sHead "</table>"
        close $sHead

    }
}

proc sBoxOwner122 {subject sPort sDir} {

    # Do for console port: 122
    set pos 0
    while {[regexp -indices -start $pos -linestop -nocase {([0-9]{4})_([0-9]{2})_i[0-9]{3}_c122} $subject offsets]==1} {
        set pos [expr {1+[lindex $offsets 1]}]
        lappend result [string range $subject [lindex $offsets 0] [lindex $offsets 1]]
    }
    set sProPortIps $result
    set result $sProPortIps
    foreach iResult $result {
        regexp "(\[0-9]{4})_(\[0-9]{2})_i(\[0-9]{3})" $iResult iTmp iPro iPort iIp
        lappend iPros $iPro
        lappend iPorts $iPort
        lappend iIps $iIp
    }

    set tPort $sPort

    if {1} {
        # Bakup up type
        set pType $sPort

        # Get server ip, console port from <show que>
        boxServer sSerPorts

        set result ""
        set subject $sSerPorts
        set pos 0
        while {[regexp -indices -start $pos -linestop -nocase "(\[0-9]+.\[0-9]+.\[0-9]+.\[0-9]+)\[ ]+\\(none\\)\[ ]+Port_(\[0-9]+)" $subject offsets]==1} {
            set pos [expr {1+[lindex $offsets 1]}]
            lappend result [string range $subject [lindex $offsets 0] [lindex $offsets 1]]
        }
        set qSerPort $result

        set result $qSerPort
        foreach iResult $result {
            regexp "(\[0-9]+.\[0-9]+.\[0-9]+.\[0-9]+)\[ ]+\\(none\\)\[ ]+Port_(\[0-9]+)" $iResult iTmp iServer iPort
            lappend qServers $iServer
  
            if {[string length $iPort] == 1} {

                set iPort 0$iPort
            }
            lappend qPorts $iPort
        }

        set nServers ""
        set qFlags ""

        foreach qServer $qServers {
             
            if {[lsearch $nServers $qServer] == -1} {
                userServer $qServer sFlag
                if {$sFlag == 1} {
                    lappend nServers $qServer
                }
            }
        }

        set tServers ""
        foreach nServer $nServers {
            boxUser $nServer sUser
            lappend tServers $sUser
        }

        set result ""
        foreach tServer $tServers {
            set subject $tServer
            set pos 0
            while {[regexp -indices -start $pos -linestop -nocase {([a-z.]+)[ ]+[0-9/a-zA-Z+:. ]+telnet[ ]+10.10.50.122+[ ]+20([0-9]+)} $subject offsets]==1} {             
                set pos [expr {1+[lindex $offsets 1]}]
                lappend result [string range $subject [lindex $offsets 0] [lindex $offsets 1]]
            }
        }
        foreach iResult $result {
            regexp {([a-z.]+)[ ]+[0-9/a-zA-Z+:. ]+telnet[ ]+[0-9.]+[ ]+20([0-9]+)} $iResult iTmp iUser iPort
            lappend bUsers $iUser
            lappend bPorts $iPort
        }

        set iUsers ""
        foreach iPort $iPorts {
            set sIndex [lsearch $bPorts $iPort]
            if {$sIndex != -1} {
                lappend iUsers [lindex $bUsers $sIndex]
            } else {
                set sIndex1 [lsearch $qPorts $iPort]
                if {$sIndex1 != -1} {
                    lappend iUsers [lindex $qServers $sIndex1]
                } else {
                    lappend iUsers "None"
                }
            }
        }

        set fobj [open $sDir/console.txt a+]
        foreach iPort $iPorts {
            puts $fobj "122_$iPort"
        }
        close $fobj

        set sHead [open $sDir/boxOwner.html a+]
        puts $sHead ""
        #puts $sHead "<table width=\"70%\" border=\"1\" cellspacing=\"1\"\
         #              cellpadding=\"1\">"

        puts ""
        #puts [format "%-15s%-15s%-15s%-15s" "User" "ConsolePort" "ConsoleIp" "Model"]
        foreach iUser $iUsers iPort $iPorts iIp $iIps iPro $iPros {

            if {[regexp "\[0-9]{4}" $tPort] == 1} {
                if {[string compare [string range $tPort 0 1] "20"] == 0} {
                    if {[string compare $tPort 20$iPort] == 0} {
                        puts [format "%-15s%-15s%-15s%-15s"  $iUser 122_20$iPort 10.10.51.$iIp $iPro]
  
                        puts $sHead "<tr>"
                        puts $sHead "<td align=\"left\"> $iUser </td>"
                        puts $sHead "<td align=\"left\"> 122_20$iPort</td>"
                        puts $sHead "<td align=\"left\"> 10.10.50.$iIp </td>"
                        puts $sHead "<td align=\"left\"> $iPro </td>"
                        puts $sHead "</tr>"

                    }
                } else {
                    if {$pType == $iPro} {
                        puts [format "%-15s%-15s%-15s%-15s"  $iUser 122_20$iPort 10.10.51.$iIp $iPro]

                        puts $sHead "<tr>"
                        puts $sHead "<td align=\"left\"> $iUser </td>"
                        puts $sHead "<td align=\"left\"> 122_20$iPort</td>"
                        puts $sHead "<td align=\"left\"> 10.10.50.$iIp </td>"
                        puts $sHead "<td align=\"left\"> $iPro </td>"
                        puts $sHead "</tr>"
                    }
                }
            } elseif {[string length $tPort] == 2} {
                if {[string compare $tPort $iPort] == 0} {
                    puts [format "%-15s%-15s%-15s%-15s"  $iUser 122_20$iPort 10.10.51.$iIp $iPro]

                    puts $sHead "<tr>"
                    puts $sHead "<td align=\"left\"> $iUser </td>"
                    puts $sHead "<td align=\"left\"> 122_20$iPort</td>"
                    puts $sHead "<td align=\"left\"> 10.10.50.$iIp </td>"
                    puts $sHead "<td align=\"left\"> $iPro </td>"
                    puts $sHead "</tr>"
                }
            } else {
               puts [format "%-15s%-15s%-15s%-15s"  $iUser 122_20$iPort 10.10.51.$iIp $iPro]

               puts $sHead "<tr>"
               puts $sHead "<td align=\"left\"> $iUser </td>"
               puts $sHead "<td align=\"left\"> 122_20$iPort</td>"
               puts $sHead "<td align=\"left\"> 10.10.50.$iIp </td>"
               puts $sHead "<td align=\"left\"> $iPro </td>"
               puts $sHead "</tr>"
            }
        }

        puts $sHead "</table>"
        close $sHead

    }
}

set sPort [lindex $argv 0]
set sDir [lindex $argv 1]
if {$sDir == ""} {
    #set sDir [pwd]
    set sDir "/var/www"
}

if {$sPort == "" || $sDir == ""} {
    puts "Please input type, (eg, all means <all boxes>, 3290 means <all 3290 boxes>, 2004 or 04 means <box 2004>!)"
    exit
} else {
   # send "ps aux | grep 'box.tcl all' | grep -v grep |  awk '{print \$13}'\r"
   # send "ps aux | grep 'box.tcl all' | grep -v grep \r"
   # expect -re "(.*)\r"
   # puts expect_out(buffer)
   # regexp "/var/www/box.tcl (all)" expect_out(buffer) sTmp sUse
   # send "exit\r"
   # break  
    puts "Please wait for 1 minute..."
    boxPortPro sCaps
    set subject $sCaps

    sBoxOwner $subject $sPort $sDir    
    sBoxOwner122 $subject $sPort $sDir    
}
