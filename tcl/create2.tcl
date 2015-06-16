#!/usr/bin/expect --

    
proc Pica8CreateConfigureAcl {  }  {

    
    set timeout 120  
    set tftp_dir  "/tmp/1.conf"
    set file [ open $tftp_dir w+ ]
    
    set config_str "
    vlan \{
    "
    puts $file "$config_str" 

    for {set i 2} {$i <= 4094} {incr i 1} {
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
    
    
    close $file
 }

 Pica8CreateConfigureAcl  
