#! /usr/bin/expect --

####################################
# Regression test main script
####################################

#####################################################
# Build topology between 40G box and the other box
#####################################################
proc sTopoBuild {sPort tPort tFlag} {

    # set timeout
    set timeout -1

    # Change the other box into Ovs mode
    userKick $tPort
    after 5000
    spawn telnet 10.10.50.122 20$tPort
    send "\r"

    while 1 {
        expect {
            "admin@XorPlus\\$" {
                send "cli\r"
            }
            "XorPlus>" {
                send "show system management-ethernet\r"
                expect -ex "show system management-ethernet"
                expect -re "(.*)XorPlus>"
                regexp {Inet addr:\s+([0-9]+.[0-9]+.[0-9]+.[0-9]+)} $expect_out(buffer) iTmp iIp
                send "exit\r"
                break
            }
        }
    }

    catch close
    catch wait

    spawn ssh $iIp -l admin

    while 1 {
        expect {
            -ex "yes/no" {
                send "yes\r"
            }
            -ex "assword" {
                send "pica8\r"
            }
            -ex "admin@" {
                send "\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "XorPlus\\$" {
                send "sudo picos_boot\r"
            }
            -ex "Enter your choice" {
                send "2\r"
            }
            "Please set a static IP and netmask for the switch" {
                send "$iIp/24\r"
            }
            "Please set the gateway IP" {
                send "[string range $iIp 0 7].1\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "admin@XorPlus" {
                send "sudo /etc/init.d/picos restart\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "admin@XorPlus" {
                send "ps aux | grep ovs\r"
                break
            }
        }
    }   

    set inOutPorts [tPortGet 5401 $tFlag]
    set inPorts [lrange $inOutPorts 0 3]
    set outPorts [lrange $inOutPorts 4 7]

    ## create ovs bridge
    foreach oCmd {"ovs-vsctl del-br br0" "ovs-vsctl add-br br0 -- set bridge br0 datapath_type=pica8"} {
        while 1 {
            expect {
                "admin@XorPlus" {
                    send "$oCmd\r"
                    break
                }
            }
        }
    }

    ## add inPorts into ovs db
    foreach inPort $inPorts {
        while 1 {
            expect {
                "admin@XorPlus" {
                    send "ovs-vsctl add-port br0 $inPort vlan_mode=trunk tag=1369 -- set Interface $inPort type=pica8 options:link_speed=1G\r"
                    break
                }
            }
        }
    }

    ## add outPorts into ovs db
    foreach outPort $outPorts {
        while 1 {
            expect {
                "admin@XorPlus" {
                    send "ovs-vsctl add-port br0 $outPort vlan_mode=trunk tag=1369 -- set Interface $outPort type=pica8\r"
                    break
                }
            }
        }
    }

    ## create static flow
    while 1 {
        expect {
            "admin@XorPlus" {
                send "ovs-ofctl del-flows br0\r"
                break
            }
        }
    }

    foreach inPort $inPorts outPort $outPorts {
        while 1 {
            expect {
                "admin@XorPlus" {
                    send "ovs-ofctl add-flow br0 in_port=[lindex [split $inPort /] end],actions=output:[lindex [split $outPort /] end]\r"
                    break
                }
            }
        }
    }

    foreach outPort $outPorts inPort $inPorts {
        while 1 {
            expect {
                "admin@XorPlus" {
                    send "ovs-ofctl add-flow br0 in_port=[lindex [split $outPort /] end],actions=output:[lindex [split $inPort /] end]\r"
                    break
                }
            }
        }
    }

    foreach oCmd {"ovs-ofctl dump-flows br0" "ovs-appctl pica/dump-flows"} {
        while 1 {
            expect {
                "admin@XorPlus" {
                    send "$oCmd\r"
                    break
                }
            }
        }
    }

    catch close
    catch wait

    userKick $tPort
    after 5000
    spawn telnet 10.10.50.122 20$tPort
    send "\r"

    while 1 {
        expect {
            "admin@PicOS-OVS\\$" {
                send "\r"
                break
            }
            "XorPlus\\$" {
                send "exit\r"
            }
            "PicOS-OVS login:" {
                send "admin\r"
            }
            "assword:" {
                send "pica8\r"
            }
        }
    }

    catch close
    catch wait

    # Config 40G box as 4*10G mode
    ## Get the port from db
    set lPort [sPortGet 5401 $tFlag]
    set PX1 [lindex $lPort 0]
    set PX2 [lindex $lPort 1]
    set PX3 [lindex $lPort 2]
    set PX4 [lindex $lPort 3]

    userKick $sPort
    after 5000
    spawn telnet 10.10.50.122 20$sPort
    send "\r"

    while 1 {
        expect {
            "XorPlus>" {
                send "configure\r"
                break
            }
        }
    }

    if {$tFlag == 1} {

        foreach sCmd {"set interface qe-interface-mode SFP" "commit"} {
            while 1 {
                expect {
                    "XorPlus#" {
                        send "$sCmd\r"
                        break
                    }
                }
            }
        }
    
        while 1 {
            expect {
                "XorPlus#" {
                    send "run request system reboot\r"
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
                "XorPlus login:" {
                    send "admin\r"
                }
                "assword" {
                    send "pica8\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "XorPlus\\$" {
                    send "cli\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "XorPlus>" {
                    send "configure\r"
                    break
                }
            }
        }

    } else {

        while 1 {
            expect {
                "XorPlus>" {
                    send "configure\r"
                    break
                }
            }
        }
    } 

    foreach iPort "$PX1 $PX2 $PX3 $PX4" {
        while 1 {
            expect {
                "XorPlus#" {
                    send "set interface gigabit-ethernet $iPort disable false\r"
                    break
                }
            }
        }
    }

    while 1 {
        expect {
            "XorPlus#" {
                send "commit\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "XorPlus#" {
                send "exit\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "XorPlus>" {
                send "\r"
                break
            }
        }
    }

    catch close 
    catch wait
}

#####################################################
# Logout pdu 
#####################################################
proc logPduOut {sPdu} {

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

#####################################################
# Generate detail table of  fail and pass cases
#####################################################
proc dTableCase {sDir} {

    cd $sDir

    set subject ""
    exec cp bws.html dhead.html
    set file [open dhead.html r]
    while {![eof $file]} {
        set buffer [read $file 100000]
        set subject [append subject $buffer]
    }
    close $file

    set sHead [open detailHead.html w+]
    puts $sHead ""
    puts $sHead "<table width=\"100\" border=\"1\" cellspacing=\"2\"\
                       cellpadding=\"5\">"
    puts $sHead "<tr>"
    puts $sHead "<th align=\"centre\">MODULE </th>"
    puts $sHead "<th align=\"centre\">PASS</th>"
    puts $sHead "<th align=\"centre\">FAIL </th>"
    puts $sHead "<th align=\"centre\">TOTAL </th>"
    puts $sHead "</tr>"

    # Get total, pass, fail number of each module
    set sPass 0
    set sFail 0
    set sTotal 0
    set mList {CLI 802.1Q LLDP LAG/LACP Mirroring Interface FDB QinQ ECMP ACL StaticRouting Multicast VRRP SysManage QoS STP CrossFlow OVS BugVerify Vif IPv6 IPfix SFlow DHCP}
    foreach i $mList {
        set [set i](total) 0
        set [set i](pass) 0
        set [set i](fail) 0
    }

    foreach iModule {pica8CliCmd Sys8021Q pica8Lldp pica8Lacp stMirror SifFunc pica8FlowControl FdbFunc pica8Counter pica8QinQ pica8LagHash pica8EcmpHash pica8Vif pica8Acl FunStaticRoute FunIgmpSnooping FunIgmp_ pica8Vrrp pica8Storm pica8SysFunc pica8System pica8Cos pica8Portsec pica8FlexLink pica8RaGuard Ipfix sFlow funDhcpRelay pica8Mstp pica8Hybrid pica8Ovs bug} nModule {CLI 802.1Q LLDP LAG/LACP Mirroring Interface Interface FDB Interface QinQ LAG/LACP ECMP Vif ACL StaticRouting Multicast Multicast VRRP Interface SysManage SysManage QoS Interface Interface IPv6 IPfix SFlow DHCP STP CrossFlow OVS BugVerify} {

        set pos 0
        set total ""
        while {[regexp -indices -start $pos "$iModule.*?nbsp" $subject offsets]==1} {
            set pos [expr {1+[lindex $offsets 1]}]
            lappend total [string range $subject [lindex $offsets 0] [lindex $offsets 1]]
        }
        set [set nModule](total) [expr [set [set nModule](total)] + [llength $total]]

        set pos 0
        set pass ""
        while {[regexp -indices -start $pos "> pass <" $total offsets]==1} {
            set pos [expr {1+[lindex $offsets 1]}]
            lappend pass [string range $total [lindex $offsets 0] [lindex $offsets 1]]
        }
        set [set nModule](pass) [expr [set [set nModule](pass)] + [llength $pass]]

        set [set nModule](fail) [expr  [set [set nModule](total)] - [set [set nModule](pass)]]

    }

    foreach nModule $mList {

        set sPass [expr $sPass + [set [set nModule](pass)]]
        set sFail [expr $sFail + [set [set nModule](fail)]]
        set sTotal [expr $sTotal + [set [set nModule](total)]]
    }

    foreach nModule $mList {
        puts $sHead "<tr>"
        puts $sHead "<td align=\"left\"> $nModule </td>"
        puts $sHead "<td align=\"left\"> [set [set nModule](pass)] </td>"
        puts $sHead "<td align=\"left\"> [set [set nModule](fail)] </td>"
        puts $sHead "<td align=\"left\"> [set [set nModule](total)] </td>"
        puts $sHead "</tr>"

    }

    puts $sHead "<tr>"
    puts $sHead "<td align=\"left\"> All </td>"
    puts $sHead "<td align=\"left\"> [set sPass] </td>"
    puts $sHead "<td align=\"left\"> [set sFail] </td>"
    puts $sHead "<td align=\"left\"> [set sTotal] </td>"
    puts $sHead "</tr>"
    puts $sHead "</table>"

    puts $sHead "<table height=\"30\" border=\"0\" cellspacing=\"2\"\
                       cellpadding=\"5\">"
    puts $sHead "<tr>"
    puts $sHead "<td align=\"left\"> </td>"
    puts $sHead "</tr>"
    puts $sHead "</table>"

    close $sHead
}

#####################################################
# Generate table of  fail and pass cases
#####################################################
proc iTableCase {sDir uTotal uPass uFail} {

    upvar $uTotal sTotal
    upvar $uPass sPass
    upvar $uFail sFail

    cd $sDir

    set subject ""
    exec cp bws.html head.html
    set file [open head.html r]
    while {![eof $file]} {
        set buffer [read $file 100000]
        set subject [append subject $buffer]
    }
    close $file

    # Get total, pass, fail number of each module
    set sPass 0
    set sFail 0
    set sTotal 0
    set mList {CLI 802.1Q LLDP LAG/LACP Mirroring Interface FDB QinQ ECMP ACL StaticRouting Multicast VRRP SysManage QoS STP CrossFlow OVS BugVerify Vif IPv6 IPfix SFlow DHCP}
    foreach i $mList {
        set [set i](total) 0
        set [set i](pass) 0
        set [set i](fail) 0
    }


    foreach iModule {pica8CliCmd Sys8021Q pica8Lldp pica8Lacp stMirror SifFunc pica8FlowControl FdbFunc pica8Counter pica8QinQ pica8LagHash pica8EcmpHash pica8Vif pica8Acl FunStaticRoute FunIgmpSnooping FunIgmp_ pica8Vrrp pica8Storm pica8SysFunc pica8System pica8Cos pica8Portsec pica8FlexLink pica8RaGuard Ipfix sFlow funDhcpRelay pica8Mstp pica8Hybrid pica8Ovs bug} nModule {CLI 802.1Q LLDP LAG/LACP Mirroring Interface Interface FDB Interface QinQ LAG/LACP ECMP Vif ACL StaticRouting Multicast Multicast VRRP Interface SysManage SysManage QoS Interface Interface IPv6 IPfix SFlow DHCP STP CrossFlow OVS BugVerify} {
        set pos 0
        set total ""
        while {[regexp -indices -start $pos "$iModule.*?nbsp" $subject offsets]==1} {
            set pos [expr {1+[lindex $offsets 1]}]
            lappend total [string range $subject [lindex $offsets 0] [lindex $offsets 1]]
        }
        set [set nModule](total) [expr [set [set nModule](total)] + [llength $total]]

        set pos 0
        set pass ""
        while {[regexp -indices -start $pos "> pass <" $total offsets]==1} {
            set pos [expr {1+[lindex $offsets 1]}]
            lappend pass [string range $total [lindex $offsets 0] [lindex $offsets 1]]
        }
        set [set nModule](pass) [expr [set [set nModule](pass)] + [llength $pass]]

        set [set nModule](fail) [expr  [set [set nModule](total)] - [set [set nModule](pass)]]

    }

    foreach nModule $mList {

        set sPass [expr $sPass + [set [set nModule](pass)]]
        set sFail [expr $sFail + [set [set nModule](fail)]]
        set sTotal [expr $sTotal + [set [set nModule](total)]]

    }

    set sHead [open regHeader.html w+]

    set mRatio {}
    set sTmp {}
    set nTotal {}
    foreach nModule $mList {

        set nTmp [set [set nModule](total)]
  
        lappend nTotal [set [set nModule](total)]

        if {$nTmp != 0} {
            set sTmp [expr [set [set nModule](pass)] / [set [set nModule](total)].0]
        } else {
            set sTmp 0
        }
        set sTmp [format %.2f $sTmp]
        set sTmp [expr $sTmp * 100]
        set sTmp [expr int($sTmp)]
        lappend mRatio $sTmp
    }

    set sMax 10
    set sNum [expr [llength $mList]/$sMax]
    set yNum [expr [llength $mList]%$sMax]
    for {set j 0} {$j <= [expr [llength $mList]/$sMax]} {incr j} {

        if {$yNum == 0} {
            set sWid 100%
        } else {
            if {$j == [expr $sNum]} {
                set sWid [expr $yNum * 10]%
            } else {
                set sWid 100%
            }
        }

        puts $sHead "<table width=\"$sWid\" border=\"1\" cellspacing=\"0\"\ cellpadding=\"0\">"
        puts $sHead "<tr>"
        for {set i 0} {$i < $sMax} {incr i} {
            set sTmp [lindex $mList [expr $sMax*$j+$i]]
            if {$sTmp != ""} {
                puts $sHead "<th align=\"centre\" width=\"10%\"> <font size=\"2\" face=\"Arial\"> [lindex $mList [expr $sMax*$j+$i]] </font></th>"
            }
        }
        puts $sHead "</tr>"

        puts $sHead "<tr>"
        for {set i 0} {$i < $sMax} {incr i} {
            set sTmp [lindex $mRatio [expr $sMax*$j+$i]]
            if {$sTmp != ""} {
                puts $sHead "<td align=\"center\" width=\"10%\"> <font size=\"2\" face=\"Arial\">[lindex $mRatio [expr $sMax*$j+$i]]%&nbsp;&nbsp([lindex $nTotal [expr $sMax*$j+$i]])</font></td>"
            }
        }
        puts $sHead "</tr>"
        puts $sHead "</table>"

        puts $sHead "<table height=\"2\" border=\"0\" cellspacing=\"2\"\ cellpadding=\"2\">"
        puts $sHead "<tr>"
        puts $sHead "<td align=\"left\"> </td>"
        puts $sHead "</tr>"
        puts $sHead "</table>"
   }

    puts $sHead "<table height=\"30\" border=\"0\" cellspacing=\"2\"\
                       cellpadding=\"5\">"
    puts $sHead "<tr>"
    puts $sHead "<td align=\"left\"> </td>"
    puts $sHead "</tr>"
    puts $sHead "</table>"

    close $sHead
}

#####################################################
# Count the number of regression fail and pass cases
#####################################################
proc iCountRegress {tFile} {

    set iFail 0
    set iPass 0
    set iResult 0

    if {![catch {set tFile [open "$tFile" r]}]} {

        # Read a line from fd
        while {[set lineLen [gets $tFile ln]] >= 0} {
            # blank line
            if {[regexp {align.*fail} $ln]} {
                incr iFail
                continue
            } elseif {[regexp {align.*errScriptCrashed} $ln]} {
                incr iFail
                continue
            } elseif {[regexp {align.*errScriptAborted} $ln]} {
                incr iFail
                continue
            } elseif {[regexp {align.*pass} $ln]} {
                incr iPass
                continue
            }
        }

        # decide the result
        if {[expr $iFail + $iPass] > 0} {
            set iResult 1
        }

        puts "The number of failed cases is $iFail"
        puts "The number of passed cases is $iPass"
        return $iResult
    } else {
        puts "$tFile is not exist"
        return $iResult
    }
}

#####################################################                                                                                      
# Do the regression test
#####################################################
proc pica8RegressionTest {sPort sDir cIp sTopo cDir {tFlag 0}} {

    upvar $cDir cDirs

    regexp "P(\[0-9a-zA-Z]+)" $sDir sTmp sPro
    regexp "P\[0-9]+-(\[0-9]+)" $sDir sTmp sRev
    regexp "picos-(\[0-9a-zA-Z.]+)" $sDir sTmp sBr

    if {[string compare -nocase $sBr "2.0"] == 0} {
        set sBr Trunk
    }

    set uFlag 1
    set sType "XorPlus"

    if {$sTopo == 0} {
        #set runTest /home/build/automation/run/daily$sPro
        set runTest /home/build/automation/run/dailytridentII
    } elseif {$sTopo == 1}  {
        #set runTest /home/build/automation/run/daily$sPro
        set runTest /home/build/automation/run/dailytridentII
    } else {
        set runTest /home/build/automation/run/xorplus$sPro
    }

    if {$tFlag == 0} {
        set dbTest /home/build/automation/db/xorplus$sPro
    } else {
        set dbTest /home/build/automation/db/xorplus[set sPro]SFP
    }

    set dirDaily [exec date +%Y%m%d%H%M]_$sPro
    set headHref "http://$cIp/automation/suite/regressTest"
    set dirHref $headHref/$dirDaily/$sType/
    set cDirs "/home/build/automation/suite/regressTest/$dirDaily/$sType"

    cd /home/build/automation/suite/regressTest
    
    catch [exec mkdir $dirDaily]
    after 10000

    cd $dirDaily
    catch {exec mkdir $sType}
    cd $sType

    set sWeek [exec date +%u]
    if {$sWeek >= 6} {
        set sComment -3
    } else {
        set sComment -1
    }

    puts "sComment:$sComment dbTest:$dbTest runTest:$runTest"
    puts "=========================$sType test starts========================="
    set sWarning [catch {exec /home/build/automation/bws.tcl -n $sComment $dbTest $runTest}]
    puts "##########the sWarning is $sWarning"

    if { $sWarning == 0 } {
        set sConc PASS
        set sColor "#00FF00"
    } else {
        set sConc Fail
        set sColor "#FF0000"
    }

    dTableCase /home/build/automation/suite/regressTest/$dirDaily/$sType
    set sResult [open "detail.html" w+]
    puts $sResult "<font face=\"Arial\">\n"
    puts $sResult "<b>Date:</b>  [lindex [split $dirDaily _] 0]<br>"
    puts $sResult "<b>Model:</b>   P-$sPro<br>"
    puts $sResult "<b>Branch:</b>   $sBr<br>"
    puts $sResult "<b>Version:</b> $sRev<br>"
    puts $sResult "<b>Log location:</b> $cIp:/home/build/automation/suite/regressTest/$dirDaily/$sType<br><br>"
    puts $sResult "<HTML><BODY leftMargin=50></BODY></HTML>"
    close $sResult

    exec cat detailHead.html >> detail.html
    exec cat bws.html >> detail.html
    exec sed -i "s+<a href=\"+<a href=\"$dirHref+" detail.html

    iTableCase /home/build/automation/suite/regressTest/$dirDaily/$sType sTotal sPass sFail

    set sResult [open "sResult.html" w+]
    puts $sResult "<font face=\"Arial\">\n"
    puts $sResult "<b>Date:</b>    [lindex [split $dirDaily _] 0]<br>"
    puts $sResult "<b>Model:</b>   P-$sPro<br>"
    puts $sResult "<b>Branch:</b>   $sBr<br>"
    puts $sResult "<b>Version:</b> $sRev<br>"
    puts $sResult "<b>Total:</b>   $sTotal<br>"
    puts $sResult "<b>Pass:</b>   $sPass<br>"
    puts $sResult "<b>Fail:</b> $sFail<br>"
    puts $sResult "<b>Detail:</b> <a href=\"http://$cIp/automation/suite/regressTest/$dirDaily/$sType/detail.html\"> Detail </a><br><br>"
    puts $sResult "<HTML><BODY leftMargin=50></BODY></HTML>"
    close $sResult

    exec cat regHeader.html >> sResult.html
    exec cp sResult.html /home/build/automation/report/regression$sPro.html
    #exec cat bws.html >> sResult.html
    #exec sed -i "s+<a href=\"+<a href=\"$dirHref+" sResult.html

    if {1} {
        set sMail [open "sMail.exp" w+]
        puts $sMail "#!/bin/sh"
        puts $sMail "cat sResult.html |formail -I \"From: build@pica8.local\" \
                                               -I \"To: sqa@pica8.local\" -I \"MIME-Version:1.0\" \
                                               -I \"Content-type:text/html;charset=gb2312\" \
                                               -I \"Subject:P-$sPro Regression Test $sConc on r$sRev\"|/usr/sbin/sendmail \
                                               -oi sqa@pica8.local\n"
        close $sMail

        exec chmod 777 sMail.exp
        exec bash sMail.exp
        puts "The email will be sent!"
        after 5000
        puts "The $sType test result is sent by email to sqa@pica8.local"

        if {$uFlag == 0} {
            foreach iUser "olivier.vautrin zoneson.chen ychen" {
                exec rm sMail.exp

                set sMail [open "sMail.exp" w+]
                puts $sMail "#!/bin/sh"
                puts $sMail "cat sResult.html |formail -I \"From: ychen@pica8.com\" \
                                               -I \"To: $iUser@pica8.com\" -I \"MIME-Version:1.0\" \
                                               -I \"Content-type:text/html;charset=gb2312\" \
                                               -I \"Subject:P-$sPro Regression Test $sConc on r$sRev\"|/usr/sbin/sendmail \
                                               -f ychen@pica8.com -oi $iUser@pica8.com\n"
                close $sMail

                exec chmod 777 sMail.exp
                exec bash sMail.exp
                puts "The email will be sent!"
                after 5000
                puts "The $sType test result is sent by email to $iUser@pica8.com"
            }
        }
    }

    exec cat bws.html >> sResult.html
    exec sed -i "s+<a href=\"+<a href=\"$dirHref+" sResult.html

    puts "=========================$sType test finishes========================="
    return $sWarning
}

#####################################
# Accoring to the current server ip,
# update the automation code
######################################
proc pica8Automation {cIp} {

    spawn ssh build@$cIp

    while 1 {
        expect {
            "yes/no" {
                send "yes\r"
            }
            "assword" {
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
                send "cd /home/build/automation\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "build@" {
                send "svn info\r"
                expect -ex "svn info"
                expect -re "(.*)build@"
                regexp "Last Changed Rev:\\s+(\[0-9]+)" "$expect_out(buffer)" vTmp Version1
                send "svn up\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "mine-conflict" {
                send "mc\r"
            }
            "build@" {
                send "svn info\r"
                expect -ex "svn info"
                expect -re "(.*)build@"
                regexp "Last Changed Rev:\\s+(\[0-9]+)" "$expect_out(buffer)" vTmp Version2
                send "\r"
                break
            }
        }
    }

    send_user "Version1:$Version1 Version2:$Version2"
    if {$Version2 != $Version1} {

        while 1 {
            expect {
                "build@" {
                    send "find . -name 'tclIndex' -exec rm -rf {} \\;\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "build@" {
                    send "./build\r"
                    break
                }
            }
        }
    }

    while 1 {
        expect {
            "build@" {
                send "rm -rf test_platform/lib\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "build@" {
                send "exit\r"
                break
            }
        }
    }

    catch close
    catch wait
}

#####################################
# Accoring to the P-type,
# get the port information
######################################
proc sPortGet {sPro {tFlag 0}} {

    set sUser [exec whoami]
    if {[string compare -nocase $sUser "jenkins"] == 0} {
        set sUser "build"
    }

    if {$sPro == "3296"} {
        set sPro "3297"
    }

    if {$tFlag == 0} { 
        source /home/$sUser/automation/db/xorplus$sPro.tcl
        set sModel $sPro
    } else {
        source /home/$sUser/automation/db/xorplus[set sPro]SFP.tcl
        set sModel [set sPro]SFP
    }

    set subject [array names aSetup]
    set lPort {}
    foreach line $subject {
        if {[regexp "pica,1,lc,1,port,(\[0-9]+)" $line sTmp iPo] == 1} {
            if {$sModel == "LB9A" || $sModel == "LB9"} {
                if { $iPo <= 48 } {
                    lappend lPort "ge-1/1/$iPo"
                } else {
                    lappend lPort "te-1/1/$iPo"
                }
            } elseif {[regexp -linestop {(?:3290|3297|3295)} $sModel] == 1} {
                if { $iPo <= 48 } {
                    lappend lPort "ge-1/1/$iPo"
                } else {
                    lappend lPort "te-1/1/$iPo"
                }
            } elseif {$sModel == "LB8" || $sModel == "LY2"} {
                if { $iPo <= 48 } {
                    lappend lPort "te-1/1/$iPo"
                } else {
                    lappend lPort "qe-1/1/$iPo"
                }
            } elseif {[regexp -linestop {(?:3920|3922|3930|3924)} $sModel] == 1} {
                if { $iPo <= 48 } {
                    lappend lPort "te-1/1/$iPo"
                } else {
                    lappend lPort "qe-1/1/$iPo"
                }
            } elseif {[regexp -linestop {(?:3780)} $sModel] == 1} {
                lappend lPort "te-1/1/$iPo"
            } elseif {[regexp -linestop {(?:5101)} $sModel] == 1} {
                if { $iPo <= 40 } {
                    lappend lPort "te-1/1/$iPo"
                } else {
                    lappend lPort "qe-1/1/$iPo"
                }
            } elseif {[regexp -linestop {(?:5401SFP)} $sModel] == 1} {
                if {[regexp -linestop {(?:49|50|51|52|101|102|103|104)} $iPo] == 1} {
                    lappend lPort "qe-1/1/$iPo"
                } else {
                    lappend lPort "te-1/1/$iPo"
                }
            } elseif {[regexp -linestop {(?:5401)} $sModel] == 1} {
                lappend lPort "qe-1/1/$iPo"
            }
        }
    }

    send_user "lPort:$lPort"
    return $lPort
}

#####################################
# Accoring to the P-type,
# get the port information
######################################
proc tPortGet {sPro {tFlag 0}} {

    set sUser [exec whoami]
    if {[string compare -nocase $sUser "jenkins"] == 0} {
        set sUser "build"
    }

    if {$sPro == "3296"} {
        set sPro "3297"
    }

    if {$tFlag == 0} {
        source /home/$sUser/automation/db/xorplus[set sPro].tcl
    } else {
        source /home/$sUser/automation/db/xorplus[set sPro]SFP.tcl
    }

    if {$tFlag == 0 || $tFlag == 1} {
        set subject [array names aSetup]
        set sModel $aSetup(pica,2,sModel)
        set lPort {}
        set outPorts {}
        foreach line $subject {
            if {[regexp "pica,2,lc,1,port,(\[0-9]+),sConn" $line sTmp iPo] == 1} {
                if {$sModel == "LB9A" || $sModel == "LB9"} {
                    if { $iPo <= 48 } {
                        lappend lPort "ge-1/1/$iPo"
                    } else {
                        lappend lPort "te-1/1/$iPo"
                    }
                } elseif {[regexp -linestop {(?:3290|3297|3295)} $sModel] == 1} {
                    if { $iPo <= 48 } {
                        lappend lPort "ge-1/1/$iPo"
                    } else {
                        lappend lPort "te-1/1/$iPo"
                    }
                } elseif {$sModel == "LB8" || $sModel == "LY2"} {
                    if { $iPo <= 48 } {
                        lappend lPort "te-1/1/$iPo"
                    } else {
                        lappend lPort "qe-1/1/$iPo"
                    }
                } elseif {[regexp -linestop {(?:3920|3922|3930|3924)} $sModel] == 1} {
                    if { $iPo <= 48 } {
                        lappend lPort "te-1/1/$iPo"
                    } else {
                        lappend lPort "qe-1/1/$iPo"
                    }
                } elseif {[regexp -linestop {(?:3780)} $sModel] == 1} {
                    lappend lPort "te-1/1/$iPo"
                } elseif {[regexp -linestop {(?:5101)} $sModel] == 1} {
                    if { $iPo <= 40 } {
                        lappend lPort "te-1/1/$iPo"
                    } else {
                        lappend lPort "qe-1/1/$iPo"
                    }
                } elseif {[regexp -linestop {(?:5401SFP)} $sModel] == 1} {
                    if {[regexp -linestop {(?:49|50|51|52|101|102|103|104)} $iPo] == 1} {
                        lappend lPort "qe-1/1/$iPo"
                    } else {
                        lappend lPort "te-1/1/$iPo"
                    }
                } elseif {[regexp -linestop {(?:5401)} $sModel] == 1} {
                    lappend lPort "qe-1/1/$iPo"
                }

                if {$aSetup(pica,1,sModel) == "P5401SFP"} {
                    regexp "pica,1,1,(\[0-9])" $aSetup($sTmp) nTmp nPo 
                    if {[regexp -linestop {(?:49|50|51|52|101|102|103|104)} $nPo] == 1} {
                        lappend outPorts "qe-1/1/$nPo"
                    } else {
                        lappend outPorts "te-1/1/$nPo"
                    }
                } elseif {$aSetup(pica,1,sModel) == "P5401"} {
                    regexp "pica,1,1,(\[0-9])" $aSetup($sTmp) nTmp nPo
                    lappend outPorts "qe-1/1/$nPo"
                }
            }
        }

        set lPort "$lPort $outPorts"
        send_user "lPort: $lPort"
    }

    return $lPort
}

#####################################
# Send email
######################################
proc sEmail {sPro sBuffer sInfo sVersion} {

    set sBuffers [split $sBuffer "\n"]
    set sResult [open "sResult.html" w+]
    puts $sResult "<font face=\"Arial\">\n"
    puts $sResult "All,<br><br>"
    puts $sResult "&nbsp;&nbsp;$sInfo.<br><br>"
    puts $sResult "<br>####################################################<br>"
    puts $sResult "# Screen Capture<br>"
    puts $sResult "####################################################<br>"
    foreach sBuffer $sBuffers {
        puts $sResult "$sBuffer<br>"
    }

    puts $sResult "<br>Regards<br>"
    puts $sResult "QA<br><HTML><BODY leftMargin=50></BODY></HTML>"
    close $sResult

    set sMail [open "sMail.exp" w+]
    puts $sMail "#!/bin/sh"
    puts $sMail "cat sResult.html |formail -I \"From: build@pica8.local\" -I \"To: sqa@pica8.local\" \
                                           -I \"MIME-Version:1.0\" -I \"Content-type:text/html;charset=gb2312\" \
                                           -I \"Subject:$sInfo P-type:$sPro version:$sVersion\"|/usr/sbin/sendmail \
                                           -oi sqa@pica8.local\n"

    close $sMail

    exec chmod 777 sMail.exp
    exec bash sMail.exp
    puts "The email will be sent!"
    after 5000
    puts "The test result is sent by email to sqa@pica8.local"

}

#####################################
# According to the pdu ip, pdu port
# reboot the box
######################################
proc rPdu {iPdu iPort} {

    # reload
    if {$iPdu == "91" || $iPdu == "92" || $iPdu == "93"} {

        logPduOut $iPdu
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

        logPduOut $iPdu
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

    catch close
    catch wait
}

#####################################
# According to the console port 
# kill the user
# 1. sPort:  console port
######################################
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

#####################################
# According to the console port sPort
# get the follow information
# 1. iPort:  pdu port
# 2. sPro:   P-type
# 3. iPdu:   pdu ip
######################################
proc sProPdu {sPort iPort sPro iPdu} {

    upvar $iPort iPorts
    upvar $sPro sPros
    upvar $iPdu iPdus

    set wCmd [expr int(3*rand())]
    send_user "wCmd:$wCmd"
    if {$wCmd == 0} {
        after 5000
    } elseif {$wCmd == 1} {
        after 15000
    } else {
        after 30000
    }

    logPduOut 91
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
    catch wait

    regexp "(\[0-9a-z]+)-\[ ]\\\[--]\[ ]+(\[0-9a-z]+)_[set sPort]_" $sDbPort sTmp iPorts sPros
    if {[info exists iPorts] == 1} {
        set iPdus 91
        return
    }

    logPduOut 90
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
    catch wait

    regexp "(\[0-9]+)-\[ ]\\\[--]\[ ]+(\[0-9a-z]+)_[set sPort]_" $sDbPort sTmp iPorts sPros

    if {[info exists iPorts] == 1} {
        set iPdus 90
        puts "\nConsole port: 20$sPort P-type: $sPros Pdu_ip:$iPdus Pdu_port:$iPorts"
        return
    }

    logPduOut 92
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
    catch wait

    regexp "(\[0-9a-z]+)-\[ ]\\\[--]\[ ]+(\[0-9a-z]+)_[set sPort]_" $sDbPort sTmp iPorts sPros
    if {[info exists iPorts] == 1} {
        set iPdus 92
        puts "\nConsole port: 20$sPort P-type: $sPros Pdu_ip:$iPdus Pdu_port:$iPorts\n\n"
        return
    }

    logPduOut 93
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
    catch wait

    regexp "(\[0-9a-z]+)-\[ ]\\\[--]\[ ]+(\[0-9a-z]+)_[set sPort]_" $sDbPort sTmp iPorts sPros
    if {[info exists iPorts] == 1} {
        set iPdus 93
        return
    }
}

#####################################
# According to the Server Ip, P-type
# get the newest image
# 1. sIp:    Server Ip
# 2. sPro:   P-type
# 3. sIm:    new image location
######################################
proc sImage {sIp sPro sIm} {

    set sRel 0
    if {$sRel == 0} {
        set sDir daily
    } else {
        set sDir release
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
    send "ls -lt picos*\r"
    expect -re "(rw\[^\r]*)\r\n"
    regexp "(picos-\[0-9.a-zA-Z]+-P\[0-9]+(\[-.0-9a-zA-Z]+)?.tar.gz)" $expect_out(buffer) sTmp sIms
    send "exit\r"
    expect "logout"
    catch close
    catch wait

    set sIms "build/$sDir/$sPro/$sIms"
    puts "new image location for $sPro is: $sIms\n\n"

    return 
}

#####################################
# According to the Console port
# update the image for box 
######################################
proc sUpdate {sPort sIp iPort sPro iPdu sDir} {

    regexp "picos-(\[0-9a-zA-Z.]+)" $sDir sTmp sBr

    set timeout -1

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
        set fCmd {setenv bootargs root=/dev/ram rw console=ttyS0,115200;usb start;ext2load usb 0:2 $loadaddr boot/uImage;ext2load usb 0:2 $fdtaddr boot/p2020rdb.dtb;ext2load usb 0:2 $ramdiskaddr boot/$ramdiskfile;bootm $loadaddr $ramdiskaddr $fdtaddr}
    } elseif {$sPro == "3296" || $sPro == "3297" } {
        set fCmd {usb start;setenv bootargs root=/dev/ram rw console=ttyS0,115200;ext2load usb 0:2 $loadaddr boot/uImage;ext2load usb 0:2 $ramdiskaddr boot/$ramdiskfile;ext2load usb 0:2 $fdtaddr boot/$fdtfile;bootm $loadaddr $ramdiskaddr $fdtaddr}
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

    if {$sPro == 5401} {
        set framboot {setenv bootargs root=/dev/ram rw console=$consoledev,$baudrate $othbootargs; tftp $ramdiskaddr $base/5401/rootfs.ext2.gz.uboot;tftp $loadaddr $base/5401/uImage;tftp $fdtaddr $base/5401/p2020.dtb;bootm $loadaddr $ramdiskaddr $fdtaddr}
    }

    if {$sPro == 5101} {
        set framboot {setenv bootargs root=/dev/ram rw console=$consoledev,$baudrate $othbootargs; tftp $ramdiskaddr $base/5101/rootfs.ext2.gz.uboot;tftp $loadaddr $base/5101/uImage;tftp $fdtaddr $base/5101/p2020.dtb;bootm $loadaddr $ramdiskaddr $fdtaddr}
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
    } elseif {$sPro == "3297"} {
        set bCmd u3297
    } elseif {$sPro == "5101"} {
        set bCmd u5101
    } elseif {$sPro == "5401"} {
        set bCmd u5401
    }

    userKick $sPort
    if {$sPro == "3960"} {

    } else {

        set timeout 30

        rPdu $iPdu $iPort
        after 2000

        spawn telnet 10.10.50.122 20$sPort

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
                timeout {
                    send "\r"
                    rPdu $iPdu $iPort
                    after 2000
                }
            }
        }

        set timeout -1
 
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
                    break
                }
            }
        }

        if {$sPro == "3922" || $sPro == "3296" || $sPro == "3924" || $sPro == "5401" || $sPro == "3297" || $sPro == "5101"} {
            while 1 {
                expect {
                    -re "=>|Urus-II>|Urus2>|Cabrera2>" {
                        send "run framboot\r"
                    }
                    -re "Speed|Filename" {
                        send "\r"
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
        } elseif {$sPro == "3922"} {
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
        } elseif {$sPro == "3922" || $sPro == "3930" || $sPro == "3296" || $sPro == "3297"} {
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

        # clear buffer
        exp_send "\r"
        expect {
            -ex {input overrun} {
                send \r
                expect "*"
                match_max 10000
                expect -re ".+"
                send "\r"
                exp_continue
            }
            "*" {

            }
        }

        foreach sCmd "{rm -rf *} {udhcpc} {ping $sIp}" {
            exp_send "$sCmd\r"
            expect {
                -ex {input overrun} {
                    send \r
                    expect "*"
                    match_max 10000
                    expect -re ".+"
                    send "$sCmd\r"
                    exp_continue
                }
                -ex "$sCmd" {

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

        send \r
        expect "*"
        match_max 20000
        expect -re ".+"

        foreach sCmd "{tftp -g -r $sDir -l rootfs.tar.gz $sIp}" {
            exp_send "$sCmd\r"
            expect {
                -ex {input overrun} {
                    send \r
                    expect "*"
                    match_max 20000
                    expect -re ".+"
                    send "$sCmd\r"
                    exp_continue
                }
                -ex "tftp -g -r" {

                }
            }

        }

        send \r
        expect "*"
        match_max 20000
        expect -re ".+"

        foreach sCmd "{sync} {tar -zxvf rootfs.tar.gz} {sync}" {
            exp_send "$sCmd\r"
            expect {
                -ex {input overrun} {
                    send \r
                    expect "*"
                    match_max 20000
                    expect -re ".+"
                    send "$sCmd\r"
                    exp_continue
                }
                -ex "$sCmd" {

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

        if {$lFlag == 1 } {

            while 1 {
                expect {
                    "XorPlus login:" {
                        send "root\r"
                    }
                    "assword" {
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
                    "root@" {
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
                    "assword" {
                        send "pica8\r"
                    }
                    "XorPlus>" {
                        send "\r"
                        break
                    }
                    "Rebooting in 180 seconds" {
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
                    "successfully" {
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
                        send "\r"
                        break
                    }
                }
            }
            
            while 1 {
                expect {
                    -re "XorPlus\\$" {
                        send "cli\r"
                        break
                    }
                }
            }

            while 1 {
                expect {
                    "XorPlus>" {
                        send "set cli idle-timeout 0\r"
                        break
                    }
                }
            }

            while 1 {
                expect {
                    "XorPlus>" {
                        send "\r"
                        break
                    }
                }
            }

            catch close
            catch wait
        }
    }
}

#####################################
# According to the console port, P-type, check
# the ports status
######################################
proc pica8StatusCheck {sPort sPro {tFlag 0}} {

    # Get the port from db
    set lPort [sPortGet $sPro $tFlag]
    set PX1 [lindex $lPort 0]
    set PX2 [lindex $lPort 1]
    set PX3 [lindex $lPort 2]
    set PX4 [lindex $lPort 3]

    userKick $sPort
    after 5000
    spawn telnet 10.10.50.122 20$sPort
    send "\r"

    # Check whether the box can start up normally
    set flag 0
    set timeout 10
    while 1 {
        expect {
            "XorPlus>" {
                send "\r"
                break
            }
            timeout {
                set flag 1
                set sInfo "Box can not start up, regression test exit!"
                send "\r"
                break
            }
        }
    }

    if {$flag == 1} {
        set sBuffer {Trying 10.10.50.122...
                       Connected to 10.10.50.122.
                       Escape character is '^]'.}

        sEmail $sPro $sBuffer $sInfo "newest"
        exit
    }

    # Set speed for pure te box
    while 1 {
        expect {
            "XorPlus>" {
                send "configure\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "XorPlus#" {
                send "\r"
                break
            }
        }
    }

    foreach iPort "$PX1 $PX2 $PX3 $PX4" {
        if {[string compare [string index $PX1 0] "g"] == 0 || $sPro == "5401"} {
            break
        }

        while 1 {
            expect {
                "XorPlus#" {
                    send "set interface gigabit-ethernet $iPort speed 1000\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "XorPlus#" {
                    send "commit\r"
                    break
                }
            }
        }
    }

    while 1 {
        expect {
            "XorPlus#" {
                send "set system services telnet disable false\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "XorPlus#" {
                send "set system services telnet root-login allow\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "XorPlus#" {
                send "commit\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "XorPlus#" {
                send "set interface stm ipv4-route 6000\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "XorPlus#" {
                send "set interface stm ipv6-route 3000\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "XorPlus#" {
                send "commit\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "XorPlus#" {
                send "save running-to-startup\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "XorPlus#" {
                send "exit discard\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "XorPlus>" {
                send "request system reboot\r"
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
                break
            }
        }
    }

    while 1 {
        expect {
            "admin@" {
                send "cli\r"
            }
            "XorPlus>" {
                send "set cli idle-timeout 0\r"
                expect "*"
                match_max 100
                expect -re ".+"
                send "\r"
                break
            }
        }
    }

    # Check port is up or not
    set flag 0
    foreach iPort "$PX1 $PX2 $PX3 $PX4" {
        while 1 {
            expect {
                "XorPlus>" {
                    send "show interface gigabit-ethernet $iPort\r"
                }
                "input overrun" {
                    send "\r"
                    expect "*"
                    match_max 100
                    expect -re ".+"
                    send "\r"
                }
                "Physical link is Down" {
                    set sBuffer $expect_out(buffer)
                    set flag 1
                    send "\r"
                    break
                }
                "Physical link is Up" {
                    send "\r"
                    break
                }
            }
        }

        if {$flag == 1} {
            set sInfo "Physical link is Down, regression test exit!"
            sEmail $sPro $sBuffer $sInfo "newest"
            exit
        }
    }

    # Clear buffer
    while 1 {
        expect {
            "XorPlus>" {
                send "\r"
                expect "*"
                match_max 20000
                expect -re ".+"
                send "\r"
                break
            }
        }
    }

    # Get the port list
    set lPort ""
    while 1 {
        expect {
            "XorPlus>" {
                send "show interface brief | no-more\r"
                expect -ex "show interface brief | no-more"
                expect -re "(.*)XorPlus>"
                set subject $expect_out(buffer)
                send "\r"
                break
            }
        }
    }

    set pos 0
    while {[regexp -indices -start $pos -linestop -lineanchor {(^[gtq][-a-z0-9/]+)} $subject offsets]==1} {
        set pos [expr {1+[lindex $offsets 1]}]
        lappend lPort [string range $subject [lindex $offsets 0] [lindex $offsets 1]]
    }

    # Down the ports that are not needed
    puts "subject:$subject"
    puts "lPort:$lPort\n"

    while 1 {
        expect {
            "XorPlus>" {
                send "configure\r"
                break
            }
        }
    }

    foreach iPort $lPort {

        if {$iPort == "$PX1" || $iPort == "$PX2" || $iPort == "$PX3" || $iPort == "$PX4"} {
            continue
        }

        while 1 {
            expect {
                "XorPlus#" {
                    send "set interface gigabit-ethernet $iPort disable true\r"
                    break
                }
            }
        }

        expect {
            -ex {input overrun} {
                send \r
                expect "*"
                match_max 20000
                expect -re ".+"
                send "set interface gigabit-ethernet $iPort disable true\r"
                exp_continue
            }
            -ex "set interface gigabit-ethernet $iPort disable true" {

            }
        }

        while 1 {
            expect {
                "XorPlus#" {
                    send "commit\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "Commit OK" {
                    send "\r"
                    break
                }
            }
        }
    }

    while 1 {
        expect {
            "XorPlus#" {
                send "save running-to-startup\r"
                break
            }
        }
    }

    expect {
        -ex "XorPlus#" {
            send "exit discard\r"
            exp_continue
        }
        "XorPlus>" {
            send "exit\r"
        }
    }

    expect {
        "admin@XorPlus\\$" {
            send "sudo cp /xorplus/config/xorplus_startup.boot /cftmp\r"
        }
    }

    expect {
        "admin@XorPlus" {
            send "cli\r"
        }
    }

    expect {
        -re "XorPlus +>" {
            send "\r"
        }
    }

    catch close
    catch wait
}

#####################################
# According to test log directory, 
# generate jenkins xml report,
# scp xml report to remote server
######################################
proc regXmlReport {cIp cDir rIp rDir} {

    # Change the current dictory as sDir
    cd $cDir
 
    # Check whether the test log exist
    if {[file exists $cDir/sResult.html] == 0} {
        send_user "Test log did not exist, exit!\n"
        exit
    }

    # Read all data into one parameter for regression test log
    set subject ""
    set file [open $cDir/sResult.html r]
    while {![eof $file]} {
        set buffer [read $file 100000]
        set subject [append subject $buffer]
    } 
    close $file

    # Get the hardware 
    regexp "Model.*?P-(\[0-9]+)<br>" $subject mTmp sPro
    send_user "Hardware: $sPro\n"

    # Get the version number
    regexp "Version.*?(\[0-9]+)<br>" $subject vTmp sVersion
    send_user "Version: $sVersion\n"

    # Get all records wee need
    set pos 0
    while {[regexp -indices -start $pos {<tr>.*?</tr>} $subject offsets]==1} {
        set pos [expr {1+[lindex $offsets 1]}]
        set rTmp [string range $subject [lindex $offsets 0] [lindex $offsets 1]]
        if {[regexp "a href=" $rTmp] == 1} {
            lappend result $rTmp
        } else {
            continue
        }
    }
    send_user "\n$result\n"

    # Write the record to the xml file
    set file [open $cDir/regXmlReport.xml w]
    puts $file "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    puts $file "<report name=\"GeneratedReport-0\" categ=\"GeneratedReport\">"
    puts $file "<start>"
    puts $file "<date format=\"YYYYMMDD\" val=\"[exec date +%Y%m%d]\" />"
    puts $file "<time format=\"HHMMSS\" val=\"[exec date +%H%M]\" />"
    puts $file "</start>"
    puts $file ""

    foreach iResult $result {
       
        set pos 0
        set iRecord {}
        while {[regexp -indices -start $pos {<td.*?>.*?</td>} $iResult offsets]==1} {
            set pos [expr {1+[lindex $offsets 1]}]
            set rTmp [string range $iResult [lindex $offsets 0] [lindex $offsets 1]]
            lappend iRecord $rTmp
        }

        set iTmp [lindex $iRecord 0]
        regexp "(<a href.*>.*?</a>)" $iTmp sTmp nTmp
        regsub -all {<a.*?>(.*)</a>} $nTmp {\1} sName
        regsub -all {<td.*?>(.*)</td>} [lindex $iRecord 1] {\1} sTitle
        regsub -all {<td.*?>(.*)</td>} [lindex $iRecord 2] {\1} sTime
        regsub -all {<td.*?>(.*)</td>} [lindex $iRecord 3] {\1} sStatus

        send_user "\nsName:$sName\n"
        send_user "sTitle:$sTitle\n"
        send_user "sTime:$sTime\n"
        send_user "sStatus:$sStatus\n"

        puts $file "<test name=\"$sName\" executed=\"yes\">"
        puts $file "<description><!\[CDATA\[$sTitle]]></description>"
        puts $file "<platform name=\"PicOS\" remote=\"unknown\" capspool=\"unknown\">"
        puts $file "<hardware><!\[CDATA\[P$sPro]]></hardware>"
        puts $file "<compiler name=\"PICA8\" version=\"$sVersion\" path=\".\" />"
        puts $file "</platform>"
        puts $file "<result>"
        if {[regexp "pass" $sStatus] == 1} {
            puts $file "<success passed=\"yes\" state=\"100\" hasTimedOut=\"false\" />"
        } else {
            puts $file "<success passed=\"no\" state=\"0\" hasTimedOut=\"false\" />"
        }
        
        set sTimes [split $sTime :]
        set sHour [lindex $sTimes 0]
        if {[string index $sHour 0] == "0"} {
            set sHour [string index $sHour 1]
        }
        set sMinute [lindex $sTimes 1]
        if {[string index $sMinute 0] == "0"} {
            set sMinute [string index $sMinute 1]
        }
        set sSecond [lindex $sTimes 2]
        if {[string index $sSecond 0] == "0"} {
            set sSecond [string index $sSecond 1]
        }
        set sTime [expr $sHour * 3600 + $sMinute * 60 + $sSecond]         

        puts $file "<executiontime unit=\"s\" mesure=\"$sTime\" isRelevant=\"true\" />"
        puts $file "</result>"
        puts $file "</test>"
        puts $file ""
    }

    puts $file "</report>"
    close $file

    spawn ssh build@$cIp
    while 1 {
        expect {
            "yes/no" {
                send "yes\r"
            }
            "assword" {
                send "build\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "build@" {
                send "scp $cDir/regXmlReport.xml root@$rIp:$rDir/\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "yes/no" {
                send "yes\r"
            }
            "assword" {
                send "pica8pica8\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "build@" {
                send "exit\r"
                break
            }
        }
    }

    catch close
    catch wait
}

#####################################
# According to the console port, P-type, check
# the ports status
######################################

#####################################
# main function for the regression test
######################################
proc pica8RegressMain {sPort sIp cIp rIp rDir sTopo {tFlag 0}} {

    # According to the console port, get pdu ip, port, P-type
    sProPdu $sPort iPort sPro iPdu

    # According to the Server Ip, P-type, get new image directory
    sImage $sIp $sPro sDir

    # Update the image
    if {$sPro == "5401"} {

        # Update the image of 5401    
        sUpdate $sPort $sIp $iPort $sPro $iPdu $sDir

        # Update the image of specific box
        set sUser [exec whoami]
        if {[string compare -nocase $sUser "jenkins"] == 0} {
            set sUser "build"
        }
        if {$tFlag == 0} {
            source /home/$sUser/automation/db/xorplus[set sPro].tcl
        } else {
            source /home/$sUser/automation/db/xorplus[set sPro]SFP.tcl
        }
        regexp ",(\[0-9]+)" $aSetup(pica,2,sCslPort) csTmp tPort
        sProPdu $tPort t_iPort t_sPro t_iPdu
        sImage $sIp $t_sPro t_sDir
        sUpdate $tPort $sIp $t_iPort $t_sPro $t_iPdu $t_sDir

        # Build the topology between 5401 and the other box
        sTopoBuild $sPort $tPort $tFlag
 
    } else {

        sUpdate $sPort $sIp $iPort $sPro $iPdu $sDir
    }

    # Status Check
    if {$sPro == "5401"} {
        pica8StatusCheck $sPort $sPro $tFlag
    } else {
        pica8StatusCheck $sPort $sPro
    }

    # Update automation
    pica8Automation $cIp

    # Regression test 
    set sFlag [pica8RegressionTest $sPort $sDir $cIp $sTopo cDir $tFlag]

    # Jenkins
    regXmlReport $cIp $cDir $rIp $rDir  

    return $sFlag
}

set sPort [lindex $argv 0]
set sIp [lindex $argv 1]
set cIp [lindex $argv 2]
set rIp [lindex $argv 3]
set sTopo [lindex $argv 4]
set tFlag [lindex $argv 5]
set rDir [lindex $argv 6]

if {$sPort == "" || $sIp == "" || $cIp == "" || $rIp == "" || $rDir == "" || $sTopo == "" || $tFlag == ""} {
    puts "\n===================Usage======================"
    puts "$argv0 sPort sIp cIp rIp sTopo tFlag rDir"
    puts "===================Usage======================"
    puts "1. sPort:    the console port of the box (eg. 01 means <10.10.50.123 2001>"
    puts "2. sIp:      the ip address of server storing image (eg. 10.10.50.16)"
    puts "3. cIp:      the ip address of server doing the automation test (eg. 10.10.50.16)"
    puts "4. rIp:      the ip address of server storing xml (eg. 10.10.50.45)"
    puts "5. sTopo:    the topology selection (eg. 0 for TopologyA, 1 for TopologyB)"
    puts "5. tFlag:    the SP mode (eg. 0 menas default mode, 1 for SFP mode)"
    puts "6. rDir:     the directory of server storing xml (eg. /home/build/automation/tmp)"
    puts "\n===================Example===================="
    puts "$argv0 26 10.10.50.16 10.10.50.20 10.10.50.20 0 0 /home/build/automation"
    puts "===================Example===================="
    puts "1. sPort:       01"
    puts "2. sIp:         10.10.50.16"
    puts "3. cIp:         10.10.50.16"
    puts "4. rIp:         10.10.50.45"
    puts "5. sTopo:       0"
    puts "6. tFlag:       0"
    puts "7. rDir:        /home/build/automation/tmp"
} else {

    log_file -noappend -a /home/build/automation/suite/regressTest/regLog$sPort.txt
    set sExit [pica8RegressMain $sPort $sIp $cIp $rIp $rDir $sTopo $tFlag]
    exit $sExit
}
