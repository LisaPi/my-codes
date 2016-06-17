#! /bin/bash  
    
source './Create-xml.sh'  
put_head 'vlans xmlns="http://pica8.com/xorpplus/vlans"'  
tag_start 'vlan-id'  
#tag_start 'id'  
tag_start 'id'   
tag_value '2'
tag_end   'id' 
tag_end 'vlan-id'  
tag_end 'vlans' 

