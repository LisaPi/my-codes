#!/usr/bin/expect --

    
proc Pica8CreateConfigureFile {sip}  {

    
    set timeout 120  
    set tftp_dir  "/pica/config/admin"
    set config_acl  "
        firewall \{
            filter f33 \{
                description: \"\"
                sequence 1 \{
                    description: \"\"
                    from \{
                        source-mac-address: 11:11:11:11:11:11
                    \}
                    then \{
                        action: \"discard\"
                    \}
                \}
                input \{
                    vlan-interface vlan66
                \}
            \}
        \}"
        
    for {set i 2} {$i <= 7} {incr i 1} {
    set config_vlan "
        vlans \{
            vlan-id $i$i \{
                description: \"\"
                vlan-name: \"default\"
                l3-interface: \"\"
            \}
        \}"
    }
    
    #Write file on dir
    spawn ssh $sip -l admin
     while 1 {
        expect {
            "yes/no" {
                send "yes\r"
            }
            "assword" {
                send "pica8\r"
                break
            }
        }
    }   
    expect "admin@"
    send "pwd \r"
    expect -re "(.*)admin@(.*)"    
    send "cd /pica/config/admin\r" 
    expect -re "(.*)admin@(.*)"
    send "pwd \r"
    expect -re "(.*)admin@(.*)"
    send "echo $config_acl >>check.conf\r"
    expect -re "(.*)admin@(.*)"

    expect eof
    
       # foreach lineLic {$config_acl $config_vlan} {
           # exec echo $lineLic >> check.conf
     # }
     catch wait
     catch close
 }



 Pica8CreateConfigureFile  10.10.51.161
