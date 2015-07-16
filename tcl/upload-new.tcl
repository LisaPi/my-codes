#! /usr/bin/expect --

log_file -noappend -a upload.log

# Copy image from daily to release and generate md5 file
proc upload {sFtp sUser sPasswd sBr sVer sPro} {

    #define some global config
    global model_name
    global onie_name
    global onie_format
    global dir_name
    
    #The platform's model mapping
    set model_name [dict create "3290" "P3290" \
                                    "3295" "P3295" \
                                    "3297" "P3297" \
                                    "3296" "P3297" \
                                    "3930" "P3930" \
                                    "3920" "P3920" \
                                    "3922" "P3922" \
                                    "3924" "as5600_52x" \
                                    "3780" "P3780" \
                                    "5101" "P5101" \
                                    "5401" "P5401" \
                                    "es4654bf" "as4600_54t" \
                                    "as6701_32x" "as6701_32x" \
                                    "niagara2632xl" "niagara2632xl" \
                                    "as5712_54x" "as5712_54x" \
                                    "arctica4804i" "arctica4804i" ]
    #dir mapping                                    
    set dir_name [dict create "3290" "3290" \
                                    "3295" "3295" \
                                    "3297" "3297" \
                                    "3296" "3297" \
                                    "3930" "3930" \
                                    "3920" "3920" \
                                    "3922" "3922" \
                                    "3924" "as5600_52x" \
                                    "3780" "3780" \
                                    "5101" "5101" \
                                    "5401" "5401" \
                                    "es4654bf" "as4600_54t" \
                                    "as6701_32x" "as6701_32x" \
                                    "niagara2632xl" "niagara2632xl" \
                                    "as5712_54x" "as5712_54x" \
                                    "arctica4804i" "arctica4804i" ]    
    
    #onie name mapping  
    set onie_name [dict create "3290" "quanta_lb9a" \
                                 "3295" "quanta_lb9" \
                                 "3297" "celestica_d1012" \
                                 "3296" "celestica_d1012" \
                                 "3930" "celestica_d2030" \
                                 "3920" "quanta_ly2" \
                                 "3922" "accton_as5610_52x" \
                                 "3924" "accton_as5600_52x" \
                                 "3780" "quanta_lb8" \
                                 "5101" "foxconn_cabrera" \
                                 "5401" "foxconn_urus" \
                                 "es4654bf" "accton_as4600_54t" \
                                 "as6701_32x" "accton_as6701_32x" \
                                 "niagara2632xl" "accton_niagara2632xl" \
                                 "as5712_54x" "accton_as5712_54x" \
                                 "arctica4804i" "penguin_arctica4804i" ]
    
    #onie platform format  mapping 
    set onie_format  [dict create "3290"  "powerpc" \
                                  "3295" "powerpc" \
                                  "3297" "powerpc" \
                                  "3296" "powerpc" \
                                  "3930" "powerpc" \
                                  "3920" "powerpc" \
                                  "3922" "powerpc" \
                                  "3924" "powerpc" \
                                  "3780" "powerpc" \
                                  "5101" "powerpc" \
                                  "5401" "powerpc" \
                                  "es4654bf" "powerpc" \
                                  "as6701_32x" "powerpc" \
                                  "niagara2632xl" "x86" \
                                  "as5712_54x" "x86" \
                                  "arctica4804i" "powerpc"]                             


######Upload image 
    global model_name
    global onie_name
    global onie_format
    global dir_name
    set nPro [dict get $model_name $sPro ]
    set iPro [dict get $dir_name $sPro ]
    set onieFile [dict get $onie_name  $sPro ]  
    set onie  [dict get $onie_format  $sPro ]   
    
    regexp "(\[0-9a-zA-Z.]{3})" $sBr sTmp dBr
    set iBr [lindex [split $sBr .] 1]
    send_user "iPro:$iPro dBr:$dBr nPro:$nPro iBr:$iBr"

    #copy the packets to release dir and make md5 file
    exec cp /tftpboot/build/daily/$iPro/picos-$sBr-$nPro-$sVer.tar.gz /tftpboot/build/release/$dBr/$nPro
    exec cp /tftpboot/build/daily/$iPro/onie-installer-$onie-$onieFile-picos-$sBr-$sVer.bin /tftpboot/build/release/$dBr/$nPro
    exec cp /tftpboot/build/daily/$iPro/pica-tools-$sBr-$nPro-$sVer.deb /tftpboot/build/release/$dBr/$nPro
    exec cp /tftpboot/build/daily/$iPro/pica-linux-$sBr-$nPro-$sVer.deb /tftpboot/build/release/$dBr/$nPro 
    exec cp /tftpboot/build/daily/$iPro/pica-switching-$sBr-$nPro-$sVer.deb /tftpboot/build/release/$dBr/$nPro
    exec cp /tftpboot/build/daily/$iPro/pica-ovs-$sBr-$nPro-$sVer.deb /tftpboot/build/release/$dBr/$nPro         
    cd /tftpboot/build/release/$dBr/$nPro       
    exec md5sum picos-$sBr-$nPro-$sVer.tar.gz >> picos-$sBr-$nPro-$sVer.tar.gz.md5

     #upload  packets to ftp
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
                 send "put picos-$sBr-$nPro-$sVer.tar.gz.md5 ./picos-$sBr-$nPro-$sVer.tar.gz.md5\r"
                 break
             }
         }
     }

     while 1 {
         expect {
             "ftp>" {
                 send "put picos-$sBr-$nPro-$sVer.tar.gz ./picos-$sBr-$nPro-$sVer.tar.gz\r"
                 break
             }
         }
     }

    while 1 {
          expect {
              "ftp>" {
                  send "put onie-installer-$onie-$onieFile-picos-$sBr-$sVer.bin ./onie-installer-$onie-$onieFile-picos-$sBr-$sVer.bin\r"
                  break
              }
          }
     }

    while 1 {
         expect {
             "ftp>" {
                 send "put pica-switching-$sBr-$nPro-$sVer.deb ./pica-switching-$sBr-$nPro-$sVer.deb\r"
                 break
             }
         }
     }

     while 1 {
         expect {
             "ftp>" {
                 send "put pica-ovs-$sBr-$nPro-$sVer.deb ./pica-ovs-$sBr-$nPro-$sVer.deb\r"
                 break
             }
         }
     }

    while 1 {
         expect {
             "ftp>" {
                 send "put pica-linux-$sBr-$nPro-$sVer.deb ./pica-switching-$sBr-$nPro-$sVer.deb\r"
                 break
             }
         }
     }

     while 1 {
         expect {
             "ftp>" {
                 send "put pica-tools-$sBr-$nPro-$sVer.deb ./pica-ovs-$sBr-$nPro-$sVer.deb\r"
                 break
             }
         }
     }

     while 1 {
         expect {
             "ftp>" {
                 send "chmod 777 ./pica-switching-$sBr-$nPro-$sVer.deb\r"
                 break
             }
         }
     }

     while 1 {
         expect {
             "ftp>" {
                 send "chmod 777 ./pica-ovs-$sBr-$nPro-$sVer.deb\r"
                 break
             }
         }
     }

     while 1 {
         expect {
             "ftp>" {
                 send "chmod 777 ./pica-linux-$sBr-$nPro-$sVer.deb\r"
                 break
             }
         }
     }

     while 1 {
         expect {
             "ftp>" {
                 send "chmod 777 ./pica-tools-$sBr-$nPro-$sVer.deb\r"
                 break
             }
         }
     }
   
     while 1 {
         expect {
             "ftp>" {
                 send "chmod 777 ./picos-$sBr-$nPro-$sVer.tar.gz.md5\r"
                 break
             }
         }
     }

     while 1 {
         expect {
             "ftp>" {
                 send "chmod 777 ./picos-$sBr-$nPro-$sVer.tar.gz\r"
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
    puts "6. sPro:     the model of box"
    puts "\n===================Example===================="
    puts "$argv0 ftp.pica8.org engineer@pica8.org development@bj8 2.6 20907 \"3290 3295 3780 3920 3922 3930 3296 5401 3924 5101\""
    puts "===================Example===================="
    puts "\n"
} else {
    upload $sFtp $sUser $sPasswd $sBr $sVer $sPro
}
