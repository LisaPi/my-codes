#!/usr/bin/expect


proc GetDefineimage {sPro sVer sRev } {

      set sIp 10.10.50.16
      set sUser build
      set sPaw build
      
      spawn ssh $sIp -l $sUser
      while 1 {
          expect {
             "yes/no" {
                 send "yes\r"
              }
              "assword" {
                 send "$sPaw\r"
                 break
              }
          }
      }
      
      while 1 {
         expect {
            "$sUser@" {
                send "cd /tftpboot/build/daily/$sPro\r"
                expect -re "$sUser@"
                send "ls -lt picos*$sVer*18*.tar.gz\r"
                expect -ex {ls -lt}
                expect -re "(.*)$sUser@"
                set subject $expect_out(buffer)
                send "exit\r"
                break                
             }
          }
       }
       
       puts "------$subject------"
       set sImages [split $subject \r\n] 
       puts "===$sImages==="      
       foreach sIm $sImages {
           puts "sIm: $sIm" 
           set flag [regexp -linestop -lineanchor "picos-$sVer-(?:\[-a-zA-Z0-9]+)-(\[0-9]+).tar.gz" $sIm result sVersion] 
           if {$flag == 1} {
               if {$sVersion < $sRev} {
                   break
               }
           }
       }

      catch close
      catch wait

      puts "sVersion:$sVersion"
      return $sVersion
}

GetDefineimage  3290  2.5 18664

