#!/bin/bash

. /etc/functions

#get picos version
version() 
{
    res=`grep DISTRIB_RELEASE /etc/lsb-release|awk -F'=' '{print $2}'`
    echo $res
}

#get picos revision
revision()
{
    res=`grep DISTRIB_REVISION /etc/lsb-release|awk -F'svn' '{print $2}'`
    echo $res
}

#get serial number
serial_number()
{
    res=`/pica/bin/system/fan_status -s|grep MotherBoard|awk '{print $NF}'`
    echo $res
}

#get management port(eth0 mac address)
managemnet_port_mac()
{
    res=`ifconfig eth0|grep HWaddr|awk '{print $NF}'`
    echo $res
}

#get switch mac address
switch_mac()
{
    res=`/pica/bin/system/pica_switch_mac`
    echo $res
}

#syslog messages
#$1: log facility and priority
#$2: messages
send_syslog_message()
{
   facility=local0
   prompt="[ZTP]"
   msg=$prompt" "$2
   if [ "$1" == "info" ]; then
       logger -p $facility.info "$msg"
       return $?
   elif [ "$1" == "err" ]; then
       logger -p $facility.err "$msg"
       return $?
   elif [ "$1" == "warn" ]; then
       logger -p $facility.warn "$msg"
       return $?
   elif [ "$1" == "crit" ]; then
       logger -p $facility.crit "$msg"
       return $?
   elif [ "$1" == "notice" ]; then
       logger -p $facility.notice "$msg"
       return $?
   elif [ "$1" == "emerg" ]; then
       logger -p $facility.emerg "$msg"
       return $?
   elif [ "$1" == "alert" ]; then
       logger -p $facility.alert "$msg"
       return $?
   elif [ "$1" == "debug" ]; then
       logger -p $facility.debug "$msg"
       return $?
   fi
   return 1
       
}

syslog_info()
{
   send_syslog_message "info" $1
   return $?
}

syslog_err()
{
   send_syslog_message "err" $1
   return $?
}

syslog_debug()
{
   send_syslog_message "debug" $1
   return $?
}

syslog_warn()
{
   send_syslog_message "warn" $1
   return $?
}


#get tftp server ip address
get_tftp_server_ip()
{
    #get the server name info from lease file
    for i in `ls /var/lib/dhcp/` 
    do
        #the option name maybe tftp-server-name
        res=`grep -a tftp-server-name /var/lib/dhcp/$i`
        if [ "$res" != "" ]; then
            break
        fi
        #the option name maybe server-name
        res=`grep -a server-name /var/lib/dhcp/$i`
        if [ "$res" != "" ]; then
            break
        fi
    done
    #only return last one result, which is the new one
    res=`echo $res|tail -1 |tr -d ";"|awk ' {print $NF}'`
    
    if [ $res == "" ]; then
        syslog_err "Can not find TFTP server IP address"
    else
        syslog_info "TFTP server Ip address:$res"
    fi
    echo $res
            
}

#get scripts name
get_scripts_name()
{
    #get the scripts name info from lease file
    for i in `ls /var/lib/dhcp/`
    do
        #the option name maybe bootfile-name
        res=`grep -a bootfile-name /var/lib/dhcp/$i`
        if [ "$res" != "" ]; then
            break
        fi
        #the option name maybe filename
        res=`grep -a filename /var/lib/dhcp/$i`
        if [ "$res" != "" ]; then
            break
        fi
    done
    #only return last one result, which is the new one
    res=`echo $res|tail -1 |tr -d ";"|awk ' {print $NF}'`
    if [ $res == "" ]; then
        syslog_err "Can not find boot file name"
    else
        syslog_info "Boot file name:$res"
    fi
    echo $res
}

#check partition status
check_p2_status()
{
    res=`grep secondary /etc/picos/fs_status|awk '{print $NF}'`
    if [ $res -ne "ok" -a $res -ne  "up-to-date" ]; then
        return 0
    else
        syslog_err "Partiton 2 is not ready" 
        return 1
    fi
}

#check the picos service settings
#return xorpplus/ovs
check_picos_settings()
{
    res=`grep picos_start /etc/picos/picos_start.conf|awk -F'=' '{print $2}'`
    echo $res
    
}

#check picos service
#$1: xorp/ovs
#return: 0:running, 1/2:fail, not running
check_picos_status()
{
    if [ "$1"  == "xorpplus" ]; then
        res=`/etc/init.d/picos status|grep xorp|grep failed|wc -l`
    elif [ "$1" == "ovs" ]; then
        res=`/etc/init.d/picos status|grep ovs|grep failed|wc -l`
    else
        res=1
    fi
    return $res
}

#change the settings of picos service
#$1: the server selected, 1/2/3
#$2: a static IP and netmask for the switch (e.g. 128.0.0.10/24)
#$3: the gateway IP (e.g 172.168.1.2)
change_picos_settings()
{
    #check the param firstly
    if [ "$1" -eq "1" ]; then
        sed -i 's/\(.*\)picos_start=\(.*\)/picos_start=xorpplus/g' /etc/picos/picos_start.conf
        res=$?
    elif [ "$1" -eq "2" ]; then
        is_v4_ipnet ${2}
        res_1=$?
        is_v4_ip ${3}
        res_2=$?
        if [ $res_1 -eq 0 -a $res_2 -eq 0 ]; then
            switch_ovs_ip_add=`echo $2 | awk -F '/' '{print $1}'`
            switch_ovs_ip_net=`echo $2 | awk -F '/' '{print $2}'`
            switch_ovs_ip_netmask=$(calcult_netmask ${switch_ovs_ip_net})
            sed -i 's/\(.*\)picos_start=\(.*\)/picos_start=ovs/g' /etc/picos/picos_start.conf
            sed -i "s/\(.*\)ovs_switch_ip_address=\(.*\)/ovs_switch_ip_address=$switch_ovs_ip_add/g" /etc/picos/picos_start.conf
            sed -i "s/\(.*\)ovs_switch_ip_netmask=\(.*\)/ovs_switch_ip_netmask=$switch_ovs_ip_netmask/g" /etc/picos/picos_start.conf
            sed -i "s/\(.*\)ovs_switch_gateway_ip=\(.*\)/ovs_switch_gateway_ip=$gateway_ovs_ip/g" /etc/picos/picos_start.conf
            res=0
        else
            res=1
        fi          
               
    elif [ "$1" -eq "3" ]; then
       sed -i 's/\(.*\)picos_start=\(.*\)/picos_start=/g' /etc/picos/picos_start.conf
       res=$?
    else
       res=1
    fi
   
    return $res
    
}

#start/stop/restat picos service
picos_start_stop()
{
    if [ "$1" -ne "" ]; then
        if [ "$1" == "start" ]; then
            /etc/init.d/picos start
            res=$?
        elif [ "$1" == "stop" ]; then
            /etc/init.d/picos stop
            res=$?
        elif [ "$1" == "restart" ]; then
            /etc/init.d/picos restart
            res=$?
        elif [ "$1" == "status" ]; then
            /etc/init.d/picos status
            res=$?
        else
            res=1
        fi
    else
        res=1
    fi
    return $res
}

#start PicOS L2/L3 
picos_xorp_start() 
{
    res=$(check_picos_settings)
    if [ "$res" != "xorpplus" ]; then
       change_picos_settings 1
       if [ $? -eq 1 ]; then
          return 1
       fi
    fi
   
    #check whther xorpplus is runnning
    check_picos_status xorpplus
    if [ $? -eq 0 ]; then
        #xorpplus is running
        return 0
    fi

    #check whether ovs  is running
    check_picos_status ovs
    if [ $? -eq 0 ]; then
        #ovs is running, we restart the picos service
        picos_start_stop restart
        if [ $? -ne 0 ]; then
            syslog_err "PicOS service restart failed"
        fi
        return $?
    fi

    #start xorpplus
    picos_start_stop start

    if [ $? -ne 0 ]; then
        syslog_err "PicOS XorPlus service start failed"
    fi
    return $?
    
}

#start PicOS OVS
picos_ovs_start()
{
    res=$(check_picos_settings)
    if [ "$res" -ne "ovs" ]; then
       change_picos_settings 2 
       if [ $? -eq 1 ]; then
          return 1
       fi
    fi

    #check whther xorpplus is runnning
    check_picos_status xorpplus
    if [ $? -eq 0 ]; then
        #xorpplus is running
        picos_start_stop restart
        if [ $? -ne 0 ]; then
            syslog_err "PicOS service restart failed"
        fi
        return $?
    fi

    #check whether ovs is running
    check_picos_status ovs
    if [ $? -eq 0 ]; then
        #ovs is running, return 0
        return 0
    fi
       
    #start xorpplus
    picos_start_stop start  
    if [ $? -ne 0 ]; then
        syslog_err "PicOS OVS service start failed"
    fi
    return $?

}

#get file from tftp server
#$3: tftp server ip address
#$1: file name in tftp server
#$2: file name with path in local;
#return value: 0 when success, 1 when fail
tftp_get_file()
{   
    if [ "$3" == "" ]; then
        server_ip=$(get_tftp_server_ip)
    else
        server_ip=$3
    fi
    if [ "$2" != ""  -a "$3" != "" -a "$server_ip" != "" ]; then
        atftp --option "blksize 4096" -g -r $1 -l $2 $server_ip >/dev/null 2>&1
        if [ $? -eq 0 ]; then
            res=0
        else
            res=1
            rm -fr $2
        fi
    else
        res=1
    fi
    
    echo $res
}

#get the scripts of provision from tftp server
#0 when success, and 1 when fail
tftp_get_scripts()
{
    sever_ip=$(get_tftp_server_ip)
    scripts_file=$(get_scripts_name)
    if [ "$server_ip" != "" -a "$scripts_file" != "" ]; then
        res=$(tftp_get_file ${scripts_file} "/cftmp/provision.sh" ${sever_ip}) 
    else
        res=1
    fi

    if [ "$res" -eq "0" ]; then
        syslog_info "Download ZTP file success, saved in /cftmp/provision.sh"
        chmod +x /cftmp/provision.sh
        res=$?
    else
        syslog_err "Download ZTP file failed"
    fi
    echo $res
}

#get xorp configuration files
#1:remote configuration files
#2:sever ip address
#0 when success, and 1 when fail
tftp_get_xorp_config_files()
{
    if [ "$2" == "" ]; then
        server_ip=$(get_tftp_server_ip)
    else
        server_ip=$2
    fi
    res=$(tftp_get_file $1 "/cftmp/pica.conf" ${sever_ip})
    
    if [ "$res" -eq "0" ]; then
        syslog_info "Download Xorp Confiugration file success"
        mv /cftmp/pica.conf /pica/config/pica.conf
        res=$?
    else 
        syslog_err "Download Xorp Confiugration file failed"
    fi
    
    return $res
}

#get ovs configuration files
#1:remote configuration files
#2:sever ip address
#0 when success, and 1 when fail
tftp_get_ovs_config_files()
{
    if [ "$2" == "" ]; then
        server_ip=$(get_tftp_server_ip)
    else
        server_ip=$2
    fi
    res=$(tftp_get_file $1 "/cftmp/ovs-vswitchd.conf.db" ${sever_ip})

    if [ "$res" -eq "0" ]; then
        syslog_info "Download OVS Configuration file success"
        mv /cftmp/ovs-vswitchd.conf.db /ovs/ovs-vswitchd.conf.db
        res=$?
    else
        syslog_err "Download OVS Configuration file failed"
    fi

    return $res
}


#get picos service configuration files
#1:remote configuration files
#2:sever ip address
#0 when success, and 1 when fail
tftp_get_picos_config_files()
{
    if [ "$2" == "" ]; then
        server_ip=$(get_tftp_server_ip)
    else
        server_ip=$2
    fi
    res=$(tftp_get_file $1 "/cftmp/picos_start.conf" ${sever_ip})
    
    if [ "$res" -eq "0" ]; then
        syslog_info "Download PicOS Configuration file success"
        mv /cftmp/picos_start.conf /etc/picos/picos_start.conf
        res=$?
    else
        syslog_err "Download PicOS Configuration file failed"
    fi

    return $res
}

#get picos image
#$1:remote image name
#$2:sever ip address
#0 when success, and 1 when fail
tftp_get_picos_image()
{
    if [ "$2" == "" ]; then
        server_ip=$(get_tftp_server_ip)
    else
        server_ip=$2
    fi
    res=$(tftp_get_file $1 "/cftmp/rootfs.tar.gz" ${sever_ip})

    if [ "$res" -eq "0" ]; then
        syslog_info "Download PicOS image success"
    else
        syslog_err "Download PicOS image failed"
    fi
    return $res
}

#get pica image
#$1:remote image name
#$2:sever ip address
#0 when success, and 1 when fail
tftp_get_pica_image()
{
   if [ "$2" == "" ]; then
        server_ip=$(get_tftp_server_ip)
    else
        server_ip=$2
    fi
    res=$(tftp_get_file $1 "/cftmp/pica.tar.gz" ${sever_ip})

    if [ "$res" -eq "0" ]; then
        syslog_info "Download Pica image success"
    else
        syslog_err "Download Pica image failed"
    fi

    return $res
}



