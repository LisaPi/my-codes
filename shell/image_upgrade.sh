#!/bin/bash

read -p "server ip address:" server_ip

echo "$server_ip"

ping $server_ip -c 1 > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "Can not connect to $server_ip"
    exit 1
fi

echo "Connect to $server_ip succeed"

module=`version | grep P- | tr -d " " | tr -d "HardwareModel:"`

while [ x"$file_path" == x"" ]; do
   read -p "File path:" path
   if [ `expr index "$path" "$module"` -ne 0 ]; then
       file_path=$path
   else
       echo "WRONG SWITCH - you are trying to update $module with $path file, Please use the correct tar"
   fi
done

echo "Upgrade $module with $file_path";


echo "Please select the way to download image from server"
echo "    [1] SCP"
echo "    [2] FTP"
echo "    [3] Tftp"
while [  x"$choice" == x"" ]; do
    read -p "Enter your choice (1,2,3):" choice_sel
    if [ "$choice_sel" == "1" -o "$choice_sel" == "2" -o "$choice_sel" == 3 ]; then
        choice=$choice_sel
    else
        echo "Your input is not correct"
    fi
done

if [ "$choice" -eq 1 ]; then
   echo "Using SCP to download image"

elif [ "$choice" -eq 2 ]; then
   echo "Using ftp to download image"

elif [ "$choice" -eq 3 ]; then
   echo "Using tftp to download image"

else
   echo "Your select is not correct"
fi



