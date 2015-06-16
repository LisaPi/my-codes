#!/usr/bin/expect --

   
   set timeout 5
   set tftp_dir "/home/tftpboot"
   
   #delete the make file on tftp
   exec rm -rf $tftp_dir/none.conf

