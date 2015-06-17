#!/usr/bin/env expect

# define global config
global quotes
global sdk_dir
global kernel_dir
global ppc_dir
global box_dir
global box_name
global os_dir
global rel_dir 
global cross_dir
global cross_dir1
global image_name
global model_name
global onie_name
global onie_format 
global ovs_model_name

#pica-xorplus mappig 
set quotes [dict create "1.1" "xorplus" \
                        "2.6" "pica" \
                        "2.6B" "xorplus" \
                        "verizon" "xorplus"]
                        
#sdk mapping  
set sdk_dir [dict create "3290" "sdk-xgs-robo-6.3.2" \
                        "3295" "sdk-xgs-robo-6.3.2" \
                        "3297" "sdk-xgs-robo-6.3.2" \
                        "3296" "sdk-xgs-robo-6.3.2" \
                        "3930" "sdk-xgs-robo-6.3.2" \
                        "3920" "sdk-xgs-robo-6.3.2" \
                        "3922" "sdk-xgs-robo-6.3.2" \
                        "3924" "sdk-xgs-robo-6.3.2" \
                        "3780" "sdk-xgs-robo-6.3.2" \
                        "5101" "sdk-xgs-robo-6.3.2" \
                        "5401" "sdk-xgs-robo-6.3.2" \
                        "es4654bf" "sdk-xgs-robo-6.3.2" \
                        "as6701_32x" "sdk-xgs-robo-6.3.2" \
                        "niagara2632xl" "sdk-xgs-robo-6.3.9" \
                        "as5712_54x" "sdk-xgs-robo-6.3.9" \
                        "arctica4804i" "sdk-xgs-robo-6.3.2" ]
                                             
#kernel mapping  
set kernel_dir [dict create "3290" "linux-2.6.27-lb9a" \
                           "3295" "linux-2.6.27-lb9a" \
                           "3297" "linux-2.6.32-pronto3296" \
                           "3296" "linux-2.6.32-pronto3296" \
                           "3930" "linux-2.6.32.24-lb8d" \
                           "3920" "linux-2.6.32.24-lb8d" \
                           "3922" "linux-2.6.32.13-pronto3922" \
                           "3924" "linux-3.4.82" \
                           "3780" "linux-2.6.27-lb9a" \
                           "5101" "linux-3.4.82" \
                           "5401" "linux-3.0.48-pronto5401" \
                           "es4654bf" "linux-3.4.82" \
                           "as6701_32x" "linux-3.4.82" \
                           "niagara2632xl" "linux-3.4.82-x86_64" \
                           "as5712_54x" "linux-3.4.82-x86_64" \
                           "arctica4804i" "linux-3.2.35-onie" ]
                   
#powerpc mapping 
set ppc_dir  [dict create "1.1" "rootfs-debian-basic" \
                          "2.6" "rootfs-debian-basic" \
                          "2.6B" "rootfs-debian-basic" \
                          "verizon" "rootfs-debian-basic" ]
                                  

#box pronto mapping  
set box_dir [dict create "3290" "pronto3290" \
                        "3295" "pronto3295" \
                        "3297" "pronto3296" \
                        "3296" "pronto3296" \
                        "3930" "pronto3930" \
                        "3920" "pronto3920" \
                        "3922" "pronto3922" \
                        "3924" "pronto3924" \
                        "3780" "pronto3780" \
                        "5101" "pronto5101" \
                        "5401" "pronto5401" \
                        "es4654bf" "es4654bf" \
                        "as6701_32x" "as6701_32x" \
                        "niagara2632xl" "niagara2632xl" \
                        "as5712_54x" "as5712_54x" \
                        "arctica4804i" "arctica4804i" ]
                        
# box mapping   
set box_name [dict create "3290" "p3290" \
                           "3295" "p3295" \
                           "3297" "p3296" \
                           "3296" "p3296" \
                           "3930" "p3930" \
                           "3920" "p3920" \
                           "3922" "p3922" \
                           "3924" "p3924" \
                           "3780" "p3780" \
                           "5101" "p5101" \
                           "5401" "p5401" \
                           "es4654bf" "es4654bf" \
                           "as6701_32x" "as6701_32x" \
                           "niagara2632xl" "niagara2632xl" \
                           "as5712_54x" "as5712_54x" \
                           "arctica4804i" "arctica4804i" ]

#image model name 
set image_name [dict create "3290" "P3290" \
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

#image dir model name                   
set model_name [dict create "3290" "3290" \
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

#ovs dir model name 
set ovs_model_name [dict create "3290" "3290new" \
                                      "3295" "3295new" \
                                      "3297" "3296new" \
                                      "3296" "3296new" \
                                      "3930" "3930" \
                                      "3920" "3920new" \
                                      "3922" "3922new" \
                                      "3924" "3924" \
                                      "3780" "3780new" \
                                      "5101" "5101" \
                                      "5401" "5401" \
                                      "es4654bf" "es4654bf" \
                                      "as6701_32x" "as6701_32x" \
                                      "niagara2632xl" "niagara2632xl" \
                                      "as5712_54x" "as5712_54x" \
                                      "arctica4804i" "arctica4804i" ]
                        
   
#onie foramt  mapping  
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


#onie platform foramt  mapping 
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

#os dir mapping 
set os_dir [dict create "1.1" "os-dev" \
                        "2.6" "os-dev" \
                        "2.6B" "os-dev" \
                        "verizon" "os-dev" ]

#relative dir mapping 
set rel_dir  [dict create "1.1" "." \
                        "2.6" "." \
                        "2.6B" "." \
                        "verizon" "."  ]
                        
#CROSS_COMPILE mapping 
set cross_dir [dict create "3290" "powerpc-linux" \
                           "3295" "powerpc-linux" \
                           "3297" "powerpc-linux-gnuspe" \
                           "3296" "powerpc-linux-gnuspe" \
                           "3930" "powerpc-linux-gnuspe" \
                           "3920" "powerpc-linux-gnuspe" \
                           "3922" "powerpc-linux-gnuspe" \
                           "3924" "powerpc-linux-gnuspe" \
                           "3780" "powerpc-linux-gnuspe" \
                           "5101" "powerpc-linux-gnuspe" \
                           "5401" "powerpc-linux-gnuspe" \
                           "es4654bf" "powerpc-linux-gnuspe" \
                           "as6701_32x" "powerpc-linux-gnuspe" \
                           "niagara2632xl" "" \
                           "as5712_54x" "" \
                           "arctica4804i" "powerpc-linux-gnuspe" ]
                           
#CROSS_COMPILE mapping 
set cross_dir1 [dict create "3290" "powerpc-linux-" \
                            "3295" "powerpc-linux-" \
                            "3297" "powerpc-linux-gnuspe-" \
                            "3296" "powerpc-linux-gnuspe-" \
                            "3930" "powerpc-linux-gnuspe-" \
                            "3920" "powerpc-linux-gnuspe-" \
                            "3922" "powerpc-linux-gnuspe-" \
                            "3924" "powerpc-linux-gnuspe-" \
                            "3780" "powerpc-linux-gnuspe-" \
                            "5101" "powerpc-linux-gnuspe-" \
                            "5401" "powerpc-linux-gnuspe-" \
                            "es4654bf" "powerpc-linux-gnuspe-" \
                            "as6701_32x" "powerpc-linux-gnuspe-" \
                            "niagara2632xl" "" \
                            "as5712_54x" "" \
                            "arctica4804i" "powerpc-linux-gnuspe-" ]


                        

######Clean/up  svn
proc imageRmSvn {sName sDir sIp sType sBox} {

    regexp "branches/(\[-.0-9a-zA-Z]+)" $sDir sTmp sBrs    
    set timeout -1
    set sDirs $sDir
    global sdk_dir
    global kernel_dir
    global ppc_dir
    global box_dir
    global os_dir
    global rel_dir 
    set sLib [dict get $sdk_dir $sBox ]
    set oDir [dict get $os_dir  $sBrs ]  
    set hTmp [dict get $rel_dir  $sBrs ] 
    set eBox [dict get $box_dir  $sBox ] 
    set sPow [dict get $ppc_dir  $sBrs]
    set sLin [dict get $kernel_dir  $sBox]
 
    puts "\n\n\nsBrs:$sBrs oDir:$oDir\n\n"   
    spawn ssh $sName@$sIp

    while 1 {
        expect {
            "yes/no" {
                send "yes\r"
            }
            "assword:" {
                send "$sName\r"
            }
            "$sName@" {
                send "\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "$sName@" {
                send "cd $sDirs\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "$sName@" {
                send "rm -rf $hTmp/sdk/$sLib\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "$sName@" {
                send "svn up $hTmp/sdk/$sLib\r"
                break
            }
        }
    }

    if {$sType == 0} {
        while 1 {
            expect {
                "$sName@" {
                    send "sudo rm -rf *\r"
                    break
                }
            }
        }

     while 1 {
          expect {
              "assword" {
                  send "$sName\r"
              }
              "$sName@" {
                  send "\r"
                  break
              }               
          }
      }
        
     while 1 {
            expect {
                "$sName@" {
                    send "sudo rm -rf $hTmp/$oDir/$eBox\r"
                    break
                }
            }
        }

      while 1 {
             expect {
                 "assword" {
                     send "$sName\r"
                 }
                  "$sName@" {
                      send "\r"
                      break
                 }
             }
         }

       while 1 {
              expect {                                                                                                                   
                  "$sName@" {                                                                                                              
                     send "sudo rm -rf  $hTmp/$oDir/$sPow\r"                                                                                
                     break                                                                                                              
                 }                                                                                                                      
             }                                                                                                                          
         }  

        while 1 {
            expect {
                "assword" {
                    send "$sName\r"
                }
                "$sName@" {
                    send "\r"
                    break
                }
            }
        }

       while 1 {
            expect {
                "$sName@" {
                    send "sudo rm -rf $hTmp/$oDir/linux-kernel/$sLin\r"    
                    break
                }
            }
        }

       while 1 {
            expect {
                "assword" {
                    send "$sName\r"
                }
                "$sName@" {
                    send "\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "$sName@" {
                    send "svn up\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "$sName@" {
                    send "svn up $hTmp/$oDir/$eBox\r"
                    break
                }
            }
        }
            
	while 1 {
		 expect {
			  "$sName@" {
				  send "svn up $hTmp/$oDir/$sPow\r"                                              
				  break                                                                                                                  
		     }                                                                                                                          
		 }                                                                                                                              
	  }

       while 1 {                                                                                                                      
            expect {                                                                                                                   
                "$sName@" {                                                                                                              
                    send "svn up $hTmp/$oDir/linux-kernel/$sLin\r"                                                                                     
                    break                                                                                                                  
                }                                                                                                                          
            }                                                                                                                              
        } 


    } elseif {$sType == 1} {

        while 1 {                                                                                                                          
            expect {                                                                                                                       
                "$sName@" {                                                                                                                  
                    send "svn cleanup\r"                                    
                    break                                                                                                                  
                }                                                                                                                          
            }                                                                                                                              
        }  

        while 1 {
            expect {
                "$sName@" {
                    send "svn up\r"
                    break
                }
            }
        }

	  while 1 {
		   expect {
			    "$sName@" {
				   send "svn cleanup $hTmp/$oDir/$eBox\r"
				   break
		     }
		 }
	   }

           while 1 {
               expect {
                   "$sName@" {
                       send "sudo rm -rf $hTmp/$oDir/$eBox\r"
                       break
                   }
               }
           }

            while 1 {
                expect {
                    "assword" {
                        send "$sName\r"
                    }
                    "$sName@" {
                        send "\r"
                        break
                    }
                }
            }

            while 1 {
                expect {
                    "$sName@" {
                        send "svn up $hTmp/$oDir/$eBox\r"
                        break
                    }
                }
            }

	      while 1 {                                                                                                                          
		     expect {                                                                                                                       
			    "$sName@" {                                                                                                                  
				 send "svn cleanup $hTmp/$oDir/$sPow\r"                                         
				 break                                                                                                                  
			  }                                                                                                                          
		     }                                                                                                                              
	       }  

            while 1 {
                expect {
                    "$sName@" {
                        send "svn cleanup $hTmp/$oDir/linux-kernel/$sLin\r"
                        break                                                                                                                  
                    }                                                                                                                          
                }                                                                                                                              
            }  

		while 1 {
			expect {
				"$sName@" {
					send "svn up $hTmp/$oDir/$eBox\r"
					break
			      }
			}
		 }

		while 1 {                                                                                                                          
			expect {                                                                                                                       
				"$sName@" {                                                                                                                  
					send "svn up $hTmp/$oDir/$sPow\r"                                              
					break                                                                                                                  
			  }                                                                                                                          
		    }                                                                                                                              
		}

            while 1 {
                expect {
                    "$sName@" {
                        send "svn up $hTmp/$oDir/linux-kernel/$sLin\r"
                        break                                                                                                                  
                    }                                                                                                                          
                }                                                                                                                              
            }  

    } elseif {$sType == 2} {

        while 1 {
            expect {
                "$sName@" {
                    send "\r"
                    break
                }
            }
        }
    }

    while 1 {
        expect {
            $sName@ {
                send "svn info\r"
                break
            }
        }
    }

    while 1 {
        expect {
            $sName@ {
                send "ls | grep -v os-dev | grep -v sdk | xargs chown -R $sName\r"
                break
            }
        }
    }

    while 1 {                                                                                                                              
        expect {                                                                                                                           
            $sName@ {                                                                                                                       
                send "ls | grep -v os-dev | grep -v sdk | xargs chgrp -R $sName\r"                                                          
                break                                                                                                                      
            }                                                                                                                              
        }
    }

     while 1 {
	   expect {
		$sName@ {
			send "chown -R $sName $hTmp/$oDir/$eBox\r"
			break                                                                                                                      
		}                                                                                                                              
	   }
	}

	while 1 {                                                                                                                              
	     expect {                                                                                                                           
		    $sName@ {                                                                                                                        
			 send "chgrp -R $sName $hTmp/$oDir/$eBox\r"                                                                            
			 break                                                                                                                      
		    }                                                                                                                              
	      }
	}
    
    while 1 {                                                                                                                              
        expect {                                                                                                                           
            $sName@ { 
                after 5000    
                send "\r"
                break                                                                                                                      
            }                                                                                                                              
        }
    }
}

######Get the version number 
proc  pica8GetIdNumber {sName sDir sIp} {

    set timeout 5
    set sDirs $sDir
    regexp "branches/(\[-.0-9a-zA-Z]+)" $sDirs sTmp sBrs

    spawn ssh $sName@$sIp
    send "\r"

    while 1 {
        expect {
            "yes/no" {
                send "yes\r"
            }
            "assword" {
                send "$sName\r"
            }
            "$sName@" {
                send "\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "$sName@" {
                send "grep support@pica8.org $sDir/configure.ac\r"
                expect -ex "grep support@pica8.org"
                expect -re "(.*)$sName@"
                puts $expect_out(buffer)
                regexp -linestop {pica,\s+\[([0-9a-zA-Z.]+)\]} $expect_out(buffer) rTmp rId
                send "\r"
                break
            }
        }
    }
 
    if {$sBrs == "1.1"} {
          set rId 1.1
    }
    
     return $rId                                                                                                  
} 


######Build pica
proc pica8PicaMake {sName sDir sIp sBuffer sBox sOpt sVersion rId sLic} {
  
	set timeout -1
	set sDirs $sDir
       regexp "branches/(\[-.0-9a-zA-Z]+)" $sDir sTmp sBrs   	
       global quotes
       global sdk_dir
       global kernel_dir
       global ppc_dir
       global box_dir
       global box_name
       global os_dir
       global rel_dir 
       global cross_dir
       global cross_dir1
       global image_name
       global model_name
       set sLib [dict get $sdk_dir $sBox ]
       regexp "sdk-xgs-robo-(\[-.0-9a-zA-Z]+)" $sLib sTmp sBc
       set sBcm bcm_$sBc       
       set oDir [dict get $os_dir  $sBrs ]  
       set hTmp [dict get $rel_dir  $sBrs ] 
       set eBox [dict get $box_dir  $sBox ] 
       set sPow [dict get $ppc_dir  $sBrs]
       set sLin [dict get $kernel_dir  $sBox]
       set hType [dict get $cross_dir  $sBox]
       set cType [dict get $cross_dir1  $sBox]
       set iType [dict get $quotes $sBrs]
       set mBox [dict get $box_name  $sBox ] 
       set dBox [dict get $model_name  $sBox ] 
       set tBox [dict get $image_name  $sBox ] 
       set sVasic ""
       
    # license
    if {$sLic == 0} {
        set sLicense ""
    } else {
        set sLicense "--with-license"
    }
    
    #debug   
    if {$sOpt == 1} {
        set sNoDug "--disable-debug"
        set sOpt "--enable-optimize"
        set sLoc "release"
        set sDaily "daily"
    } elseif {$sOpt == 0} {
        set sNoDug ""
        set sOpt ""
        set sLoc "debug"
        set sDaily "daily"
    } elseif {$sOpt == 2} {
        set sNoDug "--disable-debug"
        set sOpt "--enable-optimize"
        set sLoc "release"
        set sDaily "release"
    }

    upvar $sBuffer tBuffer
    set flag 0
    
    spawn ssh $sName@$sIp
    while 1 {
        expect {
            "yes/no" {
                send "yes\r"
            }
            "assword:" {
                send "$sName\r"
            }
            "$sName@" {
                send "\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "$sName@" {
                send "cd $sDirs\r"
                break                                                                                                                      
            }                                                                                                                              
        }                                                                                                                                  
    }                                                                                                                                      
                                                                                                                                           
    while 1 {
        expect {
            "$sName@" {
                send "export CROSS_COMPILE=[set cType]\r"
                break
            }
        }
    }

    while 1 {
        expect {
            $sName@ {
                send "./bootstrap\r"
                break
            } 
        }
    }



    if {$sBox == "arctica4804i"} {
         while 1 {
             expect {
                 $sName@ {
                        send "./configure --prefix=$sDirs/$hTmp/$oDir/arctica4804i/rootfs-debian/$iType \
                                          --host=$hType \
                                          --enable-static=no $sNoDug $sOpt \
                                          --with-pronto3296 \
                                          --with-lcmgr=yes $sLicense \
                                        --with-rootfs_debian=yes \
                                        ovs_cv_use_linker_sections=yes $sVasic \
                                        --with-chip_sdk_lib_path=$sDirs/pica/exlib/$sBcm.arctica4804i \
                                        --with-chip_sdk_root_path=$sDirs/$hTmp/sdk/$sLib \
                                        --with-chip_sdk_deprecated_version=no\r"
                     break
                 }
             }
         }
     } elseif {[lsearch "as5712_54x niagara2632xl" $sBox] != -1} {
            while 1 {
                expect {
                    $sName@ {
                                send "./configure --prefix=$sDirs/$hTmp/$oDir/$eBox/rootfs-debian/$iType \
                                          --host=$hType \
                                          --enable-static=no $sNoDug $sOpt \
                                          --with-$eBox \
                                          --with-lcmgr=yes $sLicense \
                                        --with-rootfs_debian=yes \
                                        ovs_cv_use_linker_sections=yes $sVasic \
                                        --with-sdk_6_3_9=yes  \
                                        --with-chip_sdk_lib_path=$sDirs/pica/exlib/$sBcm.$mBox \
                                        --with-chip_sdk_deprecated_version=no \
                                        --with-chip_sdk_root_path=$sDirs/$hTmp/sdk/$sLib\r"
                        break
                    }
                }
            }
        } else {
                 while 1 {
                        expect {
                            $sName@ {
                                send "./configure --prefix=$sDirs/$hTmp/$oDir/$eBox/rootfs-debian/$iType \
                                          --host=$hType \
                                          --enable-static=no $sNoDug $sOpt \
                                          --with-$eBox \
                                          --with-lcmgr=yes $sLicense \
                                        --with-rootfs_debian=yes \
                                        ovs_cv_use_linker_sections=yes $sVasic \
                                        --with-chip_sdk_lib_path=$sDirs/pica/exlib/$sBcm.$mBox \
                                        --with-chip_sdk_deprecated_version=no \
                                        --with-chip_sdk_root_path=$sDirs/$hTmp/sdk/$sLib\r"
                                break
                            }
                        }
                    }
                }

    while 1 {                                                                                                                              
        expect {                                                                                                                           
            $sName@ {
                send "make -j8\r" 
                break                                                                                                                      
            }                                                                                                                              
        }                                                                                                                                  
    }   

    while 1 {
        expect {
            "Error " {
                set tBuffer $expect_out(buffer) 
                puts "Image make error"
                set flag 3
                return $flag
                send "\r"
                break
            }
            $sName@ {
                send "make install\r"
                expect -ex "make install"
                send \r
                expect "*"
                match_max 50
                expect -re ".+"
                send "\r"
                break
            }
        }
    }
      
        while 1 {
            expect {
                -re "$sName@" {
                    send "cd $hTmp/$oDir/$eBox/rootfs-debian/$iType\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                -re "$sName@" {
                    send "\r"
                    break
                }
            }
        }

       while 1 {                                                                                                                          
           expect {                                                                                                                       
               $sName@ {                                                                                                                   
                    send "tar -czvf /tftpboot/$sName/$sDaily/$dBox/pica_bin-$rId-$tBox-[set sVersion].tar.gz bin/*\r"
                    expect "*"
                    match_max 100
                    expect -re ".+"
                    send "\r"
                    break                                                                                                                  
                }                                                                                                                          
            }
        }

     while 1 {
         expect {
             -re "\\\$" {
                 send "cd $sDir\r"
                 break
             }
         }
     }

     while 1 {
         expect {
             $sName@ {
                 send "make install-strip\r"
                 break
             }
         }
     }

     while 1 {
         expect {
             $sName@ {
                 send "\r"
                 break
             }                                                                                                                              
         }
     }

      while 1 {
          expect {
              $sName@ {
                  return $flag
                  break
              }
          }
      }
  }


######Build osPPC
proc osPPC {sName sDir sIp sBuffer sBox  sOpt sVersion sType rId sDep} {

	set flag 0
	set timeout -1
	upvar $sBuffer tBuffer
	set sDirs $sDir
	regexp "branches/(\[-.0-9a-zA-Z]+)" $sDir sTmp sBrs
       global quotes
       global sdk_dir
       global kernel_dir
       global ppc_dir
       global box_dir
       global box_name
       global os_dir
       global rel_dir 
       global cross_dir
       global cross_dir1
       global image_name
       global model_name
       global onie_name
       global onie_format 
       set sLib [dict get $sdk_dir $sBox ]
       regexp "sdk-xgs-robo-(\[-.0-9a-zA-Z]+)" $sLib sTmp sBc
       set sBcm bcm_$sBc       
       set oDir [dict get $os_dir  $sBrs ]  
       set hTmp [dict get $rel_dir  $sBrs ] 
       set eBox [dict get $box_dir  $sBox ] 
       set sPow [dict get $ppc_dir  $sBrs]
       set sLin [dict get $kernel_dir  $sBox]
       set hType [dict get $cross_dir  $sBox]
       set cType [dict get $cross_dir1  $sBox]
       set iType [dict get $quotes $sBrs]
       set mBox [dict get $box_name  $sBox ] 
       set dBox [dict get $model_name  $sBox ] 
       set tBox [dict get $image_name  $sBox ] 
       set lBox [string toupper $eBox]
       set lLib $sLib
       set oBox  [dict get $onie_format   $sBox ] 
       set Onie  [dict get $onie_name  $sBox ] 
       
    if {$sOpt == 1} {
        set sNoDug "--disable-debug"
        set sOpt "--enable-optimize"
        set sLoc "release"
        set sDaily "daily"
    } elseif {$sOpt == 0} {
        set sNoDug ""
        set sOpt ""
        set sLoc "debug"
        set sDaily "daily"
    } elseif {$sOpt == 2} {
        set sNoDug "--disable-debug"
        set sOpt "--enable-optimize"
        set sLoc "release"
        set sDaily "release"
    }

       
    spawn ssh $sName@$sIp
    while 1 {
        expect {
            "yes/no" {
                send "yes\r"
            }
            "assword:" {
                send "$sName\r"
            }
            "$sName@" {
                send "\r"
                break
            }
        }
    }
    
        while 1 {
            expect {
                "$sName@" {
                    send "cd $sDirs/$hTmp/$oDir/$eBox\r"
                    break
                }
            }
        }

    while 1 {                                                                                                  
        expect {                                                                                               
            $sName@  {                                                                                           
                send "export CROSS_COMPILE_PATH=/tools/eldk4.2/usr/\r"       
                break                                                                                          
            }                                                                                                  
        }                                                                                                      
    }    

    if {[lsearch "as5712_54x niagara2632xl" $sBox] == -1} {

        while 1 {
            expect {
                $sName@  {
                    send "export ARCH=powerpc\r"
                    break
                }
            }
        }
    }

    while 1 {                                                                                                                              
        expect {                                                                                                                           
            $sName@  {                                                                                                                       
                send "export CROSS_COMPILE=[set cType]\r"                                                                                               
                break                                                                                                                      
            }                                                                                                                              
        }
    }

    while 1 {
        expect {
            $sName@  {
                send "export PATH=\$CROSS_COMPILE_PATH/bin:\$PATH\r"
                break
            }
        }
    }     

       if {$sDep == 0} {
               set sDep $sVersion
       } 
       set sRevison " REVISION_NUM=$sVersion RELEASE_VER=$rId LINUX_DEB_VERSION=$rId-$sDep TOOLS_DEB_VERSION=$rId-$sDep XORP_LINUX_DEB_DEPEND_VERSION=$rId-$sDep OVS_LINUX_DEB_DEPEND_VERSION=$rId-$sDep XORP_TOOLS_DEB_DEPEND_VERSION=$rId-$sDep OVS_TOOLS_DEB_DEPEND_VERSION=$rId-$sDep"
                                                                                        
       while 1 {
              expect {
                     $sName@  {
                         send "sudo make fast $lBox=1 SDK=$sDirs/$hTmp/sdk/$lLib BRANCH=$sBrs[set sRevison]\r"
                         break
                    }
                }
            }
                    
            while 1 {
                expect {
                    $sName@ {
                        send "cp -R build_image/picos_onie_installer.bin /tftpboot/$sName/$sDaily/$dBox/onie-installer-$oBox-$Onie-picos-$rId-$sVersion.bin\r"
                        break
                    }
                }
            }

            while 1 {
                expect {
                    $sName@ {
                        send "cp -R build_image/xorplus.tar.gz /tftpboot/$sName/$sDaily/$dBox/pica-$rId-$tBox-$sVersion.tar.gz\r"
                        break
                    }
                }
            }

            while 1 {
                expect {
                    $sName@ {
                        send "cp -R build_image/rootfs.tar.gz /tftpboot/$sName/$sDaily/$dBox/picos-$rId-$tBox-$sVersion.tar.gz\r"
                        break
                    }
                }
            }

            while 1 {
                expect {
                    $sName@ {
                        send "cp -R build_image/ovs.deb /tftpboot/$sName/$sDaily/$dBox/pica-ovs-$rId-$tBox-$sVersion.deb\r"
                        break
                    }
                }
            }

            while 1 {
                expect {
                    $sName@ {
                        send "cp -R build_image/xorp.deb /tftpboot/$sName/$sDaily/$dBox/pica-switching-$rId-$tBox-$sVersion.deb\r"
                        break
                    }
                }
            }
          
            while 1 {
                expect {
                    $sName@ {
                        send "cp -R build_image/linux.deb /tftpboot/$sName/$sDaily/$dBox/pica-linux-$rId-$tBox-$sVersion.deb\r"
                        break
                    }    
                }    
            }    
      
            while 1 {
                expect {
                    $sName@ {
                        send "cp -R build_image/tools.deb /tftpboot/$sName/$sDaily/$dBox/pica-tools-$rId-$tBox-$sVersion.deb\r"
                        break
                    }
                }
            }

            while 1 {
                expect {
                    $sName@ {
                        send "\r"
                        break
                    }
                }
            }
 
            if {[lsearch "as5712_54x niagara2632xl" $sBox] != -1} {

                set sItems "{onie-installer*} {pica-*tar.gz} {pica_bin*} {ovs_bin*}  {pica-ovs*} {pica-switching*} {picos*} {pica-tools*} {pica-linux*}"

                foreach sItem $sItems {
                    while 1 {
                        expect {
                            $sName@ {
                                send "scp /tftpboot/$sName/$sDaily/$dBox/$sItem build@10.10.50.16:/tftpboot/$sName/$sDaily/$dBox/\r"
                                break
                            }
                        }
                    }

                    while 1 {
                        expect {
                            "100%" {
                                send "\r"
                                break
                            }
                            "assword" {
                                send "build\r"
                            }
                            "yes/no" {
                                send "yes\r"
                            }
                            "y/n" {
                                send "y\r"
                            }
                        }
                    }

                }

                while 1 {
                    expect {
                        $sName@ {
                            send "rm -rf /tftpboot/$sName/$sDaily/$sBox/*\r"
                            break
                        }
                    }
                }

    while 1 {
        expect {
            $sName@  {
                send "\r"
                break
            }
         }
     }
  }
    catch close
    catch wait

    return $flag
}


######Build  OVS
proc  ovsMake  {sName sDir sIp sBox oBuffer rId sLic}  {

     upvar $oBuffer oBuffers
     set timeout 5
     set sDirs $sDir
     regexp "branches/(\[-.0-9a-zA-Z]+)" $sDir sTmp sBrs
     set tOvs openvswitch-2.3.0
     set cdDirs $sDirs/ovs/$tOvs 
     set flag 0
     set sVasic ""
       global quotes
       global sdk_dir
       global kernel_dir
       global ppc_dir
       global box_dir
       global box_name
       global os_dir
       global rel_dir 
       global cross_dir
       global cross_dir1
       global image_name
       global model_name
       global ovs_model_name
       set sLib [dict get $sdk_dir $sBox ]
       regexp "sdk-xgs-robo-(\[-.0-9a-zA-Z]+)" $sLib sTmp sBc
       set sBcm bcm_$sBc              
       set oDir [dict get $os_dir  $sBrs ]  
       set hTmp [dict get $rel_dir  $sBrs ] 
       set eBox [dict get $box_dir  $sBox ] 
       set sPow [dict get $ppc_dir  $sBrs]
       set sLin [dict get $kernel_dir  $sBox]
       set hType [dict get $cross_dir  $sBox]
       set cType [dict get $cross_dir1  $sBox]
       set iType [dict get $quotes $sBrs]
       set mBox [dict get $box_name  $sBox ] 
       set dBox [dict get $model_name  $sBox ] 
       set tBox [dict get $image_name  $sBox ] 
       set pBox [dict get $ovs_model_name  $sBox ] 

    # license
    if {$sLic == 0} {
        set sLicense ""
    } else {
        set sLicense "--with-license"
    }

    spawn ssh $sName@$sIp
    send "\r"

    while 1 {
        expect {
            "yes/no" {
                send "yes\r"
                break
            }
            timeout {
                break
            }
        }
    }

    while 1 {
        expect {
            "assword" {
                send "$sName\r" 
                break
            }
        }
    }

    while 1 {
        expect {
            "$sName@" {
                send "cd $cdDirs\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "$sName@" {
                send "export CROSS_COMPILE=[set cType]\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "$sName@" {
                send "autoreconf --install --force\r"
                break
            }
        }
    }
   
    if {$sBox == "arctica4804i"} {  
         while 1 {                                                                                                                          
		expect {                                                                                                                       
			"$sName@" {                                                                                                                
				send "./configure --host=$hType $sLicense --with-pronto3296new --prefix=$sDirs/$hTmp/$oDir/pronto$sBox/rootfs-debian/ovs --with-switchdir=/ovs $sVasic\r"
				break                                                                                                                  
			}                                                                                                                          
		 }	                                                                                                                              
	  }               
      } elseif {$sBox == "es4654bf" || $sBox == "as6701_32x" || $sBox == "as5712_54x" || $sBox == "niagara2632xl"} {
 
            while 1 {
                expect {
                    "$sName@" {
                        send "./configure --host=$hType $sLicense --with-$eBox --prefix=$sDirs/$hTmp/$oDir/$eBox/rootfs-debian/ovs --with-switchdir=/ovs $sVasic\r"
                        break
                    }
                }
            }
       } else {
            while 1 {                                                                                                                      
                expect {                                                                                                                   
                    "$sName@" {                                                                                                            
                        send "./configure --host=$hType $sLicense --with-pronto$pBox --prefix=$sDirs/$hTmp/$oDir/pronto$sBox/rootfs-debian/ovs --with-switchdir=/ovs $sVasic\r"
                        break                                                                                                              
                    }                                                                                                                      
                }                                                                                                                                    
            } 
	  }
                                                                                                   

    while 1 {
        expect {
            "$sName@" {
                send "make\r"
                break
            }
        }
    }

    while 1 {                                                                                                                              
        expect {
            "Error " {
                set oBuffers $expect_out(buffer)
                puts "Image make error"
                set flag 1
                return $flag
                send "\r"
                break
            }                                                                                                                           
            "$sName@" {                                                                                                                    
                send "make install-strip\r"                                                                                                              
                break                                                                                                                      
            }                                                                                                                              
        }                                                                                                                                  
    }

    while 1 {
        expect {
            "$sName@" {
                send "make install-xlib-strip\r"
                break
            }
        }
    }

        while 1 {
            expect {
                "$sName@" {
                    send "svn info $sDir\r"
                    expect -ex {svn info}
                    expect "$sName@"
                    regexp {Last Changed Rev: ([0-9]+)} $expect_out(buffer) sTmp sVersion
                    puts "*******************sVersion  is $sVersion*************"
                    send "\r"
                    break
                }
            }
        }

        while 1 {
            expect {
                "$sName@" {
                    send "tar -czvf /tftpboot/$sName/daily/$dBox/ovs_bin-$rId-$tBox-[set sVersion].tar.gz ./vswitchd/ovs-vswitchd.dbg ./ovsdb/ovsdb-server.dbg ./utilities/ovs-appctl.dbg ./utilities/ovs-vsctl.dbg ./utilities/ovs-ofctl.dbg\r"
                    break
                }
            }
        }

    while 1 {
        expect {
            "$sName@" {
                send "\r"
                break
            }
        }
    }

	return $flag 
}


######Build oms
proc omsMake {sName sDir sIp sBox } {

    global os_dir
    regexp "branches/(\[-.0-9a-zA-Z]+)" $sDir sTmp sBrs
    set oDir [dict get $os_dir  $sBrs ]  
    set vOvs v2.0
    
    spawn ssh $sName@$sIp
    send "\r"

    while 1 {
        expect {
            "yes/no" {
                send "yes\r"
                break
            }
            timeout {
                break
            }
        }
    }

    while 1 {
        expect {
            "assword" {
                send "$sName\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "$sName@" {
                send "cd $sDir/ovs/oms\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "$sName@" {
                send "python build.py $sBox $oDir $vOvs\r"
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


#####################################################
#
# Get the version of lb9a
#
##################################################### 
proc pica8VersionGet {sName sDir sIp sBuffer} {

    set timeout 5
    set sDirs $sDir

    upvar $sBuffer tBuffer

    spawn ssh $sName@$sIp
    send "\r"

    while 1 {
        expect {
            "yes/no" {
                send "yes\r"
                break
            }
            timeout {
                break
            }
        }
    }

    while 1 {
        expect {
            "assword" {
                send "$sName\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "$sName@" {
                send "cd $sDirs\r"
                break
            }
        }
    }

    while 1 {
        expect {
            "$sName@" {
                send "svn info\r"
                expect -ex {svn info}
                expect "$sName@"
                regexp {Last Changed Rev: ([0-9]+)} $expect_out(buffer) sTmp sVersion 
                break
            }
        }
    }

    set tBuffer $expect_out(buffer)
    puts "##################################"
    puts "the buffer is $expect_out(buffer)"
    puts "##################################"
    puts "the version is $sVersion"
    return $sVersion                                                                                                    
}                                                                                                                                          

# Daily image updation
proc pica8ImageUp {sName sDir sIp sBox sType sOpt sLic sDep} {
    
    # Remove old image and update new image
    imageRmSvn $sName $sDir $sIp $sType $sBox 

    # Get the version of newly image
    set sVersion [pica8VersionGet $sName $sDir $sIp vBuffers]
    set vBuffers [split $vBuffers "\n"]

    #Get the version id  number
    set rId  [pica8GetIdNumber $sName $sDir $sIp ]

    # Get the branches name
    regexp "branches/(\[-.0-9a-zA-Z]+)" $sDir sTmp sBrs

    # Make image for pica8
    puts "##########  Pica  Make  ##########"
    set flagPica8 [pica8PicaMake $sName $sDir $sIp eBuffers $sBox $sOpt $sVersion $rId $sLic]

    if {$flagPica8 != 0} {
        set eBuffers [split $eBuffers "\n"]
        after 2000
        if {$flagPica8 == 1} {
            set imageType "Image bootstrip error of platform $sBox"
        } elseif {$flagPica8 == 2} {
            set imageType "Image configure error of platform $sBox"
        } elseif {$flagPica8 == 3}  {
            set imageType "Image make error of platform $sBox"
        } elseif {$flagPica8 == 4}  {
            set imageType "Image make install-strip error of platform $sBox"
        }

        set sResult [open "sResult.html" w+]
        puts $sResult "<font face=\"Arial\">\n"
        puts $sResult "All,<br><br>"
        puts $sResult "&nbsp;&nbsp;$imageType.<br>"
        puts $sResult "<br>####################################################<br>"
        puts $sResult "# Screen capture as follow<br>"
        puts $sResult "####################################################<br>"
        foreach eBuffer $eBuffers {
           puts $sResult "$eBuffer<br>"
        }
      
        puts $sResult "<br>####################################################<br>"
        puts $sResult "# System version<br>"
        puts $sResult "####################################################" 
        foreach vBuffer $vBuffers {
           puts $sResult "$vBuffer<br>"
        }
 
        puts $sResult "<br>Regards<br>"
        puts $sResult "QA<br><HTML><BODY leftMargin=50></BODY></HTML>"
        close $sResult

        set sMail [open "sMail.exp" w+]
        puts $sMail "#!/bin/sh"
        puts $sMail "cat sResult.html |formail -I \"From: $sName@pica8.local\" -I \"To: lpi@pica8.local\" \
                                               -I \"MIME-Version:1.0\" -I \"Content-type:text/html;charset=gb2312\" \
                                               -I \"Subject:$imageType on version $sVersion\"|/usr/sbin/sendmail -oi lpi@pica8.local\n"

        close $sMail
        exec chmod 777 sMail.exp
        exec bash sMail.exp
        exec rm -f sMail.exp
        puts "The email will be sent!"
        after 5000
        puts "The test result is sent by email to lpi@pica8.local"
        exit    
    } else {

            # ovs  Making
            puts "##########  OVS  Make  ##########"
            set flagOFlow [ ovsMake  $sName $sDir $sIp $sBox  lBuffers $rId $sLic]
            if {$flagOFlow != 0} {
                set lBuffers [split $lBuffers "\n"]
                set sResult [open "sResult.html" w+]
                puts $sResult "<font face=\"Arial\">\n"
                puts $sResult "All,<br><br>"
                puts $sResult "&nbsp;&nbsp;ovs 2.3.0 image ma
                king error.<br>"
                puts $sResult "<br>####################################################<br>"
                puts $sResult "# Screen capture as follow<br>"
                puts $sResult "####################################################<br>"
                foreach lBuffer $lBuffers {
                   puts $sResult "$lBuffer<br>"
                }

                puts $sResult "<br>####################################################<br>"
                puts $sResult "# System version<br>"
                puts $sResult "####################################################"
                foreach vBuffer $vBuffers {
                    puts $sResult "$vBuffer<br>"
                }

                puts $sResult "<br>Regards<br>"
                puts $sResult "QA<br><HTML><BODY leftMargin=50></BODY></HTML>"
                close $sResult

                set sMail [open "sMail.exp" w+]
                puts $sMail "#!/bin/sh"
                puts $sMail "cat sResult.html |formail -I \"From: $sName@pica8.local\" -I \"To: lpi@pica8.local\" \
                         -I \"MIME-Version:1.0\" -I \"Content-type:text/html;charset=gb2312\" \
                         -I \"Subject:ovs 2.3.0 image making error of platform $sBox on version $sVersion\"|/usr/sbin/sendmail -oi lpi@pica8.local\n"

                close $sMail
                exec chmod 777 sMail.exp
                exec bash sMail.exp
                exec rm -f sMail.exp
                puts "The email will be sent!"
                after 5000
                puts "The test result is sent by email to lpi@pica8.local"
                exit
            }
    }

    # oms making
    puts "##########  OMS Make  ##########"
    omsMake $sName $sDir $sIp $sBox 

    # lb9a Making
    puts "##########  osPPC  Make  ##########"
    osPPC $sName $sDir $sIp lBuffers $sBox $sOpt $sVersion $sType $rId $sDep
}

set sName [lindex $argv 0]
set sDir [lindex $argv 1]
set sIp [lindex $argv 2]
set sBox [lindex $argv 3]
set sType [lindex $argv 4]
set sOpt [lindex $argv 5]
set sLic [lindex $argv 6]
set sDep [lindex $argv 7]

if {$sName == "" || $sIp == ""  || $sDir == "" || $sBox == ""  } {
    puts "\n===================Usage======================"
    puts "$argv0 Username Directory sIp sBox sType  sOpt  sLic"
    puts "===================Usage======================"
    puts "1.  Username(Passwd should be the username)"
    puts "2.  Director:   the absolute direcotry storing code files"
    puts "3.  sIp:   the ip address of server storing code files"
    puts "4.  sBox:  3290 means <the 3290 platform> 3780 means <the 3780 platform> 3295 means <the 3295 platform>"
    puts "5.  sType:  0 means <delete,update,make>; 1 means <update,make>; 2 means <donot update,make>"   
    puts "6.  sOpt:  0 means <debug and no release>; 1 means <no debug and release>; 2 means <copy image into release>"
    puts "7.  sLic:    0 means<no license>;1 means<with license>"   
    puts "\n===================Example===================="
    puts "$argv0 build /home/build/3290/release/pica8/branches/1.1 10.10.50.16 3290 1 0 1"
    puts "===================Example===================="
    puts "1.    Username:     build"
    puts "2.    Director:    /home/build/3290/pica8/branches/1.1"
    puts "3.    sIp:         10.10.50.16"
    puts "4.    sBox:        3290"
    puts "5.    sType:       1"
    puts "6.    sOpt:        0"
    puts "7.    sLic:        1\n"
} else {
	set cUser [exec whoami]
	if {[string compare -nocase $sName $cUser] != 0} {
		puts "User:$cUser can not make the code of ower:$sName"
		exit
	}

    regexp "branches/(\[-.0-9a-zA-Z]+)" $sDir sTmp tLogs
    if {$sBox == "as6701_32x"} {
        log_file -noappend -a /home/$cUser/6701/release/pica8/[set tLogs].log
    } elseif {$sBox == "es4654bf"} {
        log_file -noappend -a /home/$cUser/4654/release/pica8/[set tLogs].log
    } elseif {$sBox == "arctica4804i"} {
        log_file -noappend -a /home/$cUser/4804/release/pica8/[set tLogs].log
    } elseif {$sBox == "3296"} {
        log_file -noappend -a /home/$cUser/3297/release/pica8/[set tLogs].log
    } elseif {$sBox == "as5712_54x"} {
        log_file -noappend -a /home/$cUser/5712/release/pica8/[set tLogs].log

        if {$sIp != "10.10.50.22"} {
            puts "5712 should be built at 10.10.50.22!"
            exit
        }
    } elseif {$sBox == "niagara2632xl"} {
        log_file -noappend -a /home/$cUser/2632/release/pica8/[set tLogs].log

        if {$sIp != "10.10.50.22"} {
            puts "2632 should be built at 10.10.50.22!"
            exit
        }
    } else {
        log_file -noappend -a /home/$cUser/$sBox/release/pica8/[set tLogs].log
    }

    if {$sLic == ""} {
        set sLic 0
    }

    if {$sDep == ""} {
        set sDep 0
    }

    pica8ImageUp $sName $sDir $sIp $sBox $sType $sOpt $sLic $sDep
}

