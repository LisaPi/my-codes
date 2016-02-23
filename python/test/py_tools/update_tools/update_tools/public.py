#!/usr/bin/env python

import os
import sys
import re
import pexpect

#User info   
user_name = 'build'
user_password = 'build'
prompt='[$#>]'

#The image dir model name mapping
dir_mode_name = {'3290':'3290',
                 '3295':'3295',
                 '3297':'3297',
                 '3922':'3922',
                 '3920':'3920',
                 '3924':'as5600_52x',
                 '3930':'3930',
                 '3780':'3780',
                 '5101':'5101',
                 '5401':'5401',
                 '4654':'as4600_54t',
                 '6701':'as6701_32x',
                 '2632':'niagara2632xl',
                 '5712':'as5712_54x',
                 '4804':'arctica4804i'}

#Image model name mapping
image_name = {'3290':'P3290',
              '3295':'P3295',
              '3297':'P3297',
              '3922':'P3922',
              '3920':'P3920',
              '3924':'as5600_52x',
              '3930':'P3930',
              '3780':'P3780',
              '5101':'P5101',
              '5401':'P5401',
              '4654':'as4600_54t',
              '6701':'as6701_32x',
              '2632':'niagara2632xl',
              '5712':'as5712_54x',
              '4804':'arctica4804i'}


#Login server via ssh
def ssh_login(server_ip=None):
    
    child = pexpect.spawn('ssh %s@%s' % (user_name, server_ip))
    child.logfile = sys.stdout
    while True:
        i = child.expect(['\$', 'yes/no', 'assword:'])
        if i == 0:
            child.sendline('')
            break
        elif i == 1:
            child.sendlist('yes')   
        else:
            child.sendline('%s' % user_password)
    
    child.expect(prompt)
    
    return child



#Kill console user(console server 10.10.50.123):(sPort:  console port) 
def userKickNew(sPort=None):

    sPrompt = ['root@','cli>','administration>']
    sCmd = ['CLI\n','administration\n','sessions\n']
    
    #login console server
    child = pexpect.spawn('ssh %s@%s' %('root','10.10.50.123'))
    child.logfile = sys.stdout
    while True:
        i = child.expect(['yes/no', 'assword:'])
        if i == 0:
            child.sendlist('yes')   
        else:
            child.sendline('%s' %('tslinux'))          
            for i in range(3): 
                child.expect(sPrompt[i])
                child.sendline(sCmd[i])
            child.expect('sessions>')
            child.sendline('kill %s\n' %sPort)
            child.expect('sessions>')
            child.sendline('quit\n')
            child.expect(sPrompt[0])
            child.sendline('exit\n')
            break
            
    child.expect(prompt) 
          
    return child


#Kill console user(console server 10.10.50.122):(sPort:  console port)  
def userKick(sPort=None):

    sPrompt = ['Username','Local','Password']
    sCmd = ['su\n','su override\n','system\n']    
    
    #login console server
    child = pexpect.spawn('telnet %s' %('10.10.50.122'))
    child.logfile = sys.stdout      
    for i in range(3): 
        child.expect(sPrompt[i])
        child.sendline(sCmd[i])
    child.expect(sPrompt[1])
    child.sendline('logout port %s\n' %sPort)
    child.expect(sPrompt[1])
    child.sendline('logput \n')    
    child.expect(prompt)  
    
    return child

    
#Expect and send   
def sendExpect(child=None, commands=None,exp_prompt=None):

    if exp_prompt is None:
        exp_prompt=prompt 
        
    for command in commands:
            child.sendline ('%s' % command)
            child.expect('(.*)%s' % exp_prompt,timeout=120)
            #print "%s%s" % (child.after,child.before)

    return child.before, child.after            


#Get the latest image
def get_new_image(server_ip=None, model=None):

    vtype='daily'    
    child = ssh_login(server_ip=server_ip)
    dest_dir = '/tftpboot/build/%s/%s' %(vtype,dir_mode_name[model])
    sendExpect(child=child, commands=['cd %s' %dest_dir])
    child.sendline('ls -lt picos*')
    child.expect('picos-([.0-9]+)-%s-([0-9]+).tar.gz' %image_name[model],timeout=120)
    image = child.match.group()
    print "******The latest image is %s******" %image
    
    return image


#Get the special image
def get_special_image(server_ip=None, model=None,revision=None):

    vtype='daily'    
    child = ssh_login(server_ip=server_ip)
    dest_dir = '/tftpboot/build/%s/%s' %(vtype,dir_mode_name[model])
    sendExpect(child=child, commands=['cd %s' %dest_dir])
    child.sendline('ls -lt picos*%s*' %revision)
    child.expect('picos-([.0-9]+)-%s-%s.tar.gz' %(image_name[model],revision),timeout=120)
    image = child.match.group()   
    print "******The special image is %s******" %image
    
    return image


#Define Uboot cmd 
def boot_cmd(model=None):

    #fCmd cmd set
    if model in ['3290','3295']: 
        fCmd = 'setenv bootargs root=/dev/ram console=ttyS0,$baudrate; bootm ffd00000 ff000000 ffee0000'
    elif model in ['3780']:
        fCmd = 'setenv bootargs root=/dev/ram console=ttyS0,$baudrate; bootm ffd00000 fef00000 ffee0000'   
    elif model in ['3920']:
        fCmd = 'setenv bootargs root=/dev/ram mtdparts=physmap-flash.0:57728k(jffs2),3968k(ramdisk),3072k(kernel),128k(dtb),128k(u-boot-env),512k(u-boot) console=ttyS0,$baudrate; bootm EFC40000 EF860000 EFF40000'
    elif model in ['3922']:
        fCmd = 'usb start;setenv bootargs root=/dev/ram rw console=$consoledev,$baudrate;ext2load usb 0:2 $ramdiskaddr $ramdiskfile;ext2load usb 0:2 $loadaddr $bootfile;ext2load usb 0:2 $fdtaddr $fdtfile;bootm $loadaddr  $ramdiskaddr $fdtaddr'
    elif model in ['3930']:
        fCmd = 'setenv bootargs root=/dev/ram rw console=ttyS0,115200;usb start;ext2load usb 0:2 $loadaddr boot/uImage;ext2load usb 0:2 $fdtaddr boot/p2020rdb.dtb;ext2load usb 0:2 $ramdiskaddr boot/rootfs.ext2.gz.uboot;bootm $loadaddr $ramdiskaddr $fdtaddr'
    elif model in ['3296','3297']:
        fCmd = 'usb start;setenv bootargs root=/dev/ram rw console=ttyS0,115200;ext2load usb 0:2 $loadaddr boot/uImage;ext2load usb 0:2 $ramdiskaddr boot/$ramdiskfile;ext2load usb 0:2 $fdtaddr boot/$fdtfile;bootm $loadaddr $ramdiskaddr $fdtaddr'
    elif model in ['5101']:
        fCmd = 'mmc rescan;setenv bootarg root=/dev/ram rw console=$consoledev,$baudrate;ext2load mmc 0:2 $loadaddr $bootfile;ext2load mmc 0:2 $fdtaddr $fdtfile;ext2load mmc 0:2 $ramdiskaddr $ramdiskfile;bootm $loadaddr $ramdiskaddr $fdtaddr'
    else:
        fCmd = ''
        
    #framboot cmd set
    if model in ['3922']:
        framboot = 'setenv bootargs root=/dev/ram rw console=$consoledev,$baudrate $othbootargs; tftp $ramdiskaddr $base/3922/rootfs.ext2.gz.uboot;tftp $loadaddr $base/3922/uImage;tftp $fdtaddr $base/3922/p2020rdb.dtb;bootm $loadaddr $ramdiskaddr $fdtaddr'
    elif model in ['3296','3297']:
        framboot = 'setenv bootargs root=/dev/ram rw console=ttyS0,115200;tftp $ramdiskaddr $base/3296/rootfs.ext2.gz.uboot;;tftp $loadaddr $base/3296/uImage;tftp $fdtaddr $base/3296/p2020rdb.dtb;bootm $loadaddr $ramdiskaddr $fdtaddr'
    elif model in ['3924']:
        framboot = 'setenv bootargs root=/dev/ram rw console=$consoledev,$baudrate;tftp $loadaddr $base/3924/uImage;tftp $fdtaddr $base/3924/p2020rdb.dtb;tftp $ramdiskaddr $base/3924/rootfs.ext2.gz.uboot;bootm $loadaddr $ramdiskaddr $fdtaddr'
    elif model in ['5101','5401']:
        framboot = 'setenv bootargs root=/dev/ram rw console=$consoledev,$baudrate $othbootargs; tftp $ramdiskaddr $base/%s/rootfs.ext2.gz.uboot;tftp $loadaddr $base/%s/uImage;tftp $fdtaddr $base/%s/p2020.dtb;bootm $loadaddr $ramdiskaddr $fdtaddr' %model
    elif model in ['6701']:
        framboot = 'setenv bootargs root=/dev/ram rw console=$consoledev,$baudrate;tftp $loadaddr $base/6700/uImage;tftp $fdtaddr $base/6700/p2020rdb.dtb;tftp $ramdiskaddr $base/6700/rootfs.ext2.gz.uboot;bootm $loadaddr $ramdiskaddr $fdtaddr'
    elif mode in ['4654']:
        framboot = 'setenv bootargs root=/dev/ram rw console=$consoledev,$baudrate;tftp $loadaddr $base/4654/uImage;tftp $fdtaddr $base/4654/p2020rdb.dtb;tftp $ramdiskaddr $base/4654/rootfs.ext2.gz.uboot;bootm $loadaddr $ramdiskaddr $fdtaddr'
    else:
        framboot = ''
        
    #bCmd cmd set
    if  model in ['3290','3295','3780','3920','3922','3930','3296','4654','3297']:
        bCmd = 'u%s' %model
    elif model in ['6701']:
        bCmd = 'u6700'
    else:
        bCmd = ''

    #picos cmd set
    
    print '########fCmd is:', fCmd 
    print '########framboot', framboot
    print '########bCmd', bCmd    
    return fCmd,framboot,bCmd

def set_env(model=None,sPort=None):

    #kill the console port
    userKick(sPort=sPort)     

    #get the uboot command
    #uboot_prompts =  ['=> ', 'LOADER=> ', "Cabrera2> ", "Urus2> "]
    
    fCmd,framboot,bCmd = boot_cmd(model=model)

    #get id 
    child = pexpect.spawn('telnet 10.10.50.122 %s' %sPort)
    if model in ['3290','3295','3780','3297']
                	"Starting Power-On Self Test" {
                	send "\003"
            	}
            	"DRAM Test" {
                	send "\025"
            	}
            	"assword" {
                	send "mercury\r"
            	}
            	"stop autoboot" {
                	send "\003\r"
            	}
            	-re "=>|Urus-II>|Urus2>|Cabrera2>" {
            	
    child.expect('')
    #child.sendline('setenv base build/uboot')
    #print "%s%s" % (child.after,child.before)

    for model in []:
    
    ##env commands
    commands = ['setenv base build/uboot',
                        'setenv ipaddr 10.10.51.77',
                        'setenv serverip 10.10.50.16',
                       'setenv gatewayip 10.10.51.1',
                        'setenv netmask 255.255.255.0',
                        'setenv fCmd \'%s\'' %fCmd,
                        'setenv framboot \'%s\'' %framboot,
                        'setenv picos \'usb start;setenv bootargs root=/dev/sda1 rw noinitrd console=$consoledev,$baudrate rootdelay=10;ext2load usb 0:1 $loadaddr boot/$bootfile;ext2load usb 0:1 $fdtaddr boot/$fdtfile;bootm $loadaddr - $fdtaddr\''
                        'setenv bootcmd \'run picos\'',
                        'saveenv']
    
    sendExpect(child=child, commands=commands,exp_prompt=uboot_prompts)


    
#def update_picos(model=None):
    

        
if __name__ == "__main__":
    #get_special_image (server_ip='10.10.50.16',model='2632',revision='21550')
    #userKickNew(sPort=8)
    #userKick(sPort=19)
    #uboot_cmd(model='3297')
    set_env(model='3297',sPort='19')