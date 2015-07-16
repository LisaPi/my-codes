#! /usr/bin/expect --

log_file -noappend -a upload.log

# Copy image from daily to release and generate md5 file
proc upload {sFtp sUser sPasswd sBr sVer sPro} {

    regexp "(\[0-9a-zA-Z.]{3})" $sBr sTmp dBr

    foreach iPro $sPro {

        if {$iPro == 3296} {
            set nPro 3297
        } else {
            set nPro $iPro
        }

        switch $iPro {
            "3290" {set onieFile "quanta_lb9a"}
            "3295" {set onieFile "quanta_lb9"}
            "3920" {set onieFile "quanta_ly2"}
            "3780" {set onieFile "quanta_lb8"}
            "3296" {set onieFile "celestica_d1012"}
            "3930" {set onieFile "celestica_d2030"}
            "3922" {set onieFile "accton_as5610_52x"}
            "3924" {set onieFile "accton_as5600_52x"}
            "4654" {set onieFile "accton_as4600_54t"}
            "6701" {set onieFile "accton_as6701_32x"}
            "5712" {set onieFile "accton_as5712_54x"}
            "5401" {set onieFile "foxconn_urus"}
            "5101" {set onieFile "foxconn_cabrera"}
        }

        set iBr [lindex [split $sBr .] 1]
        send_user "iPro:$iPro dBr:$dBr nPro:$nPro iBr:$iBr"
    
        exec cp /tftpboot/build/daily/$iPro/picos-$sBr-P$nPro-$sVer.tar.gz /tftpboot/build/release/$dBr
        exec cp /tftpboot/build/daily/$iPro/pica-switching-$sBr-P$nPro-$sVer.deb /tftpboot/build/release/$dBr
        exec cp /tftpboot/build/daily/$iPro/pica-ovs-$sBr-P$nPro-$sVer.deb /tftpboot/build/release/$dBr
 
        if {$iBr >= 4} {
            exec cp /tftpboot/build/daily/$iPro/onie-installer-powerpc-$onieFile-picos-$sBr-$sVer.bin /tftpboot/build/release/$dBr
        }

        cd /tftpboot/build/release/$dBr        
        exec md5sum picos-$sBr-P$nPro-$sVer.tar.gz >> picos-$sBr-P$nPro-$sVer.tar.gz.md5

        set timeout -1
        spawn ftp $sFtp
        while 1 {
            expect {
                "yes/no" {
                    send "yes\r"
                }
                "Name" {
                    send "$sUser\r"
                }
                "assword:" {
                    send "$sPasswd\r"
                    break
                }
            }
        }

        if {$sUser == "jenkins"} {
            while 1 {
                expect {
                    "ftp>" {
                        send "\r"
                        break
                    }
                }
            }
        } else {
            while 1 {
                expect {
                    "ftp>" {
                        send "cd /\r"
                        break
                    }
                }
            }
        }

        while 1 {
            expect {
                "ftp>" {
                    send "mkdir release-$sBr\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "ftp>" {
                    send "chmod 777 release-$sBr\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "ftp>" {
                    send "cd release-$sBr\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "ftp>" {
                    send "bin\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "ftp>" {
                    send "passive\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "ftp>" {
                    send "put picos-$sBr-P$nPro-$sVer.tar.gz.md5 ./picos-$sBr-P$nPro-$sVer.tar.gz.md5\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "ftp>" {
                    send "put picos-$sBr-P$nPro-$sVer.tar.gz ./picos-$sBr-P$nPro-$sVer.tar.gz\r"
                    break
                }
            }
        }

        if {$iBr >= 4} {
            while 1 {
                expect {
                    "ftp>" {
                        send "put onie-installer-powerpc-$onieFile-picos-$sBr-$sVer.bin ./onie-installer-powerpc-$onieFile-picos-$sBr-$sVer.bin\r"
                        break
                    }
                }
            }
        }

        while 1 {
            expect {
                "ftp>" {
                    send "put pica-switching-$sBr-P$nPro-$sVer.deb ./pica-switching-$sBr-P$nPro-$sVer.deb\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "ftp>" {
                    send "put pica-ovs-$sBr-P$nPro-$sVer.deb ./pica-ovs-$sBr-P$nPro-$sVer.deb\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "ftp>" {
                    send "chmod 777 ./picos-$sBr-P$nPro-$sVer.tar.gz.md5\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "ftp>" {
                    send "chmod 777 ./picos-$sBr-P$nPro-$sVer.tar.gz\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "ftp>" {
                    send "chmod 777 ./pica-switching-$sBr-P$nPro-$sVer.deb\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "ftp>" {
                    send "chmod 777 ./pica-ovs-$sBr-P$nPro-$sVer.deb\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "ftp>" {
                    send "exit\r"
                    break
                }
            }
        }

        catch close

    }
}

set sFtp [lindex $argv 0]
set sUser [lindex $argv 1]
set sPasswd [lindex $argv 2]
set sBr [lindex $argv 3]
set sVer [lindex $argv 4]
set sPro [lindex $argv 5]

if {$sFtp == "" || $sUser == "" || $sPasswd == "" || $sBr == "" || $sVer == "" || $sPro == ""} {
    puts "\n===================Usage======================"
    puts "$argv0 sBr sVer sPro"
    puts "===================Usage======================"
    puts "1. sFtp:     the ftp address"
    puts "2. sUser:    the user name"
    puts "3. sPasswd:  the passwd"
    puts "4. sBr:      the branches type"
    puts "5. sVer:     the version of image"
    puts "6. sPro:     the module of box"
    puts "\n===================Example===================="
    puts "$argv0 ftp.pica8.org engineer@pica8.org development@bj8 2.2.1S3 13788 \"3290 3295 3780 3920 3922 3930 3296 5401 3924 5101\""
    puts "===================Example===================="
    puts "\n"
} else {
    upload $sFtp $sUser $sPasswd $sBr $sVer $sPro
}
