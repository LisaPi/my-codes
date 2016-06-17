#! /bin/bash  
  
  
outfile=out  
tabs=0  
  
put(){  
    echo '<'${*}'>' >> $outfile  
}  

put_value() {
  echo ''${*}'' >> $outfile 
}
  
put_head(){  
    put ''${1}''  
}  
  
out_tabs(){  
    tmp=0  
    tabsstr=""  
    while [ $tmp -lt $((tabs)) ]  
    do  
        tabsstr=${tabsstr}'\t'  
        tmp=$((tmp+1))  
    done  
    echo -e -n $tabsstr >> $outfile  
}  
  
tag_start(){  
    out_tabs  
    put $1  
    tabs=$((tabs+1))  
}  
  
tag_end(){  
    tabs=$((tabs-1))  
    out_tabs  
    put '/'${1}  
}  
  
tag_value(){  
    out_tabs  
    str=""  
#    str=${1}' value="'${2}'"/'  
    str=${1} 
    put_value  $str  
} 