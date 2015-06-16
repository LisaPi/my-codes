#!/usr/bin/expect --

    
proc Pica8CreateConfigureAcl {  }  {

    
    set timeout 120  
    set tftp_dir  "/tmp/1.conf"
    set file [ open $tftp_dir w+ ]
    
    set config_str "
    vlan \{
    "
    puts $file "$config_str" 

    for {set i 2} {$i <= 2} {incr i 1} {
    set config_vlan "
            vlan-id $i \{
                description: \"\"
                vlan-name: \"default\"
                l3-interface: \"\"
           \}"
     puts $file "$config_vlan"      
     }
    
    set config_end "
  \}
    "
    puts $file "$config_end"
    
    set config_str1 "
   firewall \{
       filter f1 \{
           description: \"\""
    puts $file "$config_str1"   
    
    for {set j 1} {$j <= 2} {incr j 1} {
    set config_acl "        sequence $i \{
                description: \"\"
                from \{
                    source-address-ipv4: 192.168.$j.1/24
                \}
                then \{
                    action: \"forward\"
                \}
            \}"
    puts $file "$config_acl"          
    }
    
    set config_end1 "
        \}
    \}"    
    
    puts $file "$config_end1"
    close $file
 }

 Pica8CreateConfigureAcl  
