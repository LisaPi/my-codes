
#!/bin/bash

. /etc/functions


# to do:
#    - dynamic create p2files.lst: usr/lib
# in extracting partition image in rc_ap2:
#   build_p2_image "/mnt/sd_card" "/mnt/sd_card/cftmp/p2" "/mnt/sd_card/usr/lib/python2.7/dist-packages/pica8/p2files.lst" 
# after partition system starts:
#   build_p2_image "" "/cftmp/p2" "/usr/lib/python2.7/dist-packages/pica8/p2files.lst"

umount_partition1()
{
    mount -t proc proc /proc
    sleep 2
    umount /mnt/usb/sys
    umount /mnt/usb/proc
    umount /mnt/usb/run/lock
    umount /mnt/usb/run/shm
    umount /mnt/usb/run
    umount /mnt/usb/tmp
    sleep 2
    umount /mnt/usb/dev/pts
}

save_environment()
{
    cp ./usr/lib/python2.7/dist-packages/pica8/provision-target.lst ./cftmp/provision-target.lst.tmp
    #cp ./var/lib/dhcp/dhclient.leases ./cftmp/dhclient.leases.tmp
    if [ -f ./etc/picos/fs_status ]; then
        cp ./etc/picos/fs_status ./cftmp/fs_status.tmp
    else
        echo "secondary: new" > ./cftmp/fs_status.tmp
    fi
}

restore_environment()
{
    mv ./cftmp/provision-target.lst.tmp ./usr/lib/python2.7/dist-packages/pica8/provision-target.lst
    #mv ./cftmp/dhclient.leases.tmp ./var/lib/dhcp/dhclient.leases
    mv ./cftmp/fs_status.tmp ./etc/picos/fs_status
}

# umount old file system
umount_partition1
sleep 2

cd /mnt/usb

# save environment
save_environment

ls |grep -v cftmp|xargs rm -fr
mv ./cftmp/rootfs.tar.gz .
sync
sleep 2

# extract partition 1 file system
tar -xzvf rootfs.tar.gz

# restore environment
restore_environment

echo "wait a minute, sync the data to disk ..."
sync
rm rootfs.tar.gz
sleep 2
echo " "
sync

# build 2nd partition image if os version changes
echo "building new partition 2 image ..."
build_partition2_image "." "./cftmp/p2" "./etc/picos/p2files.lst"
# mark partition 2 as ready with clean image
set_fs_status "secondary" "./etc/picos" "ready-clean"

if [ -f /boot/rootfs.ext2.gz.uboot ]; then
    cp /boot/rootfs.ext2.gz.uboot ./cftmp/p2/boot/
fi

echo "new partition 2 image ready"

echo "Image upgrading finished. Restart now ..."
echo " "
reboot
