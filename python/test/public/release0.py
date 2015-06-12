#! /usr/bin/env python

"""
Created on 2015-06-12
@author: lisapi
The script is used to copy images from daily dir to release dir and create md5 file

"""


#import some lib
import pexpect
import sys
import re
import os
import pxssh
from time import sleep
import api

# Build platform model dir name mapping
dir_model_name = {'3290': '3290',
               '3295': '3295',
               '3297': '3297',
               '3922': '3922',
               '3920': '3920',
               '3924': 'as5600_52x',
               '3930': '3930',
               '3780': '3780',
               '5401': '5401',
               '5101': '5101',
               'es4654bf': 'as4600_54t',
               'as6701_32x': 'as6701_32x',
               'niagara2632xl': 'niagara2632xl',
               'as5712_54x': 'as5712_54x',
               'arctica4804i': 'arctica4804i'}

# Build image name mapping
image_model_name = {'3290': 'P3290',
               '3295': 'P3295',
               '3297': 'P3297',
               '3922': 'P3922',
               '3920': 'P3920',
               '3924': 'as5600_52x',
               '3930': 'P3930',
               '3780': 'P3780',
               '5401': 'P5401',
               '5101': 'P5101',
               'es4654bf': 'as4600_54t',
               'as6701_32x': 'as6701_32x',
               'niagara2632xl': 'niagara2632xl',
               'as5712_54x': 'as5712_54x',
               'arctica4804i': 'arctica4804i'}

# Onie image name  mapping
onie_name_map = {'3290': 'quanta_lb9a',
               '3295': 'quanta_lb9',
               '3297': 'celestica_d1012',
               '3922': 'accton_as5610_52x',
               '3920': 'quanta_ly2',
               '3924': 'accton_as5600_52x',
               '3930': 'celestica_d2030',
               '3780': 'quanta_lb8',
               '5101': 'foxconn_cabrera',
               '5401': 'foxconn_urus',
               'es4654bf': 'accton_as4600_54t',
               'as6701_32x': 'accton_as6701_32x',
               'niagara2632xl': 'accton_niagara2632xl',
               'as5712_54x': 'accton_as5712_54x',
               'arctica4804i': 'penguin_arctica4804i'}


#User/Server  info
user_name= "build"
user_password = 'build'
server_ip = '10.10.50.16'

#Copy image to release dir and create md5 file
def main(model=None,branch_name=None,sRevision=None,sDr=None):

    #login server
    child = api.ssh_login(ip=server_ip,user=user_name,password=user_password)
    print "*********************"

    #create dir
    cmd = [ 'cd /tftpboot/build/release/',
                'mkdir %s' %(sDr)]
    for icmd in cmd:            
        api.sendExpect(child=child, command=icmd) 
        
    #copy image
    for model_name in model:
        if model_name in ['as5712_54x', 'niagara2632xl']:
            platform = 'x86'
        else:
            platform = 'powerpc'
        print "platform is %s" %platform    
        commands = [
                    'cd /tftpboot/build/release/%s' %(sDr),
                    'mkdir %s' %(image_model_name[model_name]),
                    'cp /tftpboot/build/daily/%s/picos-%s-%s-%s.tar.gz /tftpboot/build/release/%s/%s' % (dir_model_name[model_name],branch_name,image_model_name[model_name],sRevision,sDr,image_model_name[model_name]),
                    'cp /tftpboot/build/daily/%s/pica-switching-%s-%s-%s.deb /tftpboot/build/release/%s/%s' %(dir_model_name[model_name],branch_name,image_model_name[model_name],sRevision,sDr,image_model_name[model_name]),
                    'cp /tftpboot/build/daily/%s/pica-ovs-%s-%s-%s.deb /tftpboot/build/release/%s/%s' %(dir_model_name[model_name],branch_name,image_model_name[model_name],sRevision,sDr,image_model_name[model_name]),
                    'cp /tftpboot/build/daily/%s/pica-linux-%s-%s-%s.deb /tftpboot/build/release/%s/%s' %(dir_model_name[model_name],branch_name,image_model_name[model_name],sRevision,sDr,image_model_name[model_name]),
                    'cp /tftpboot/build/daily/%s/pica-tools-%s-%s-%s.deb /tftpboot/build/release/%s/%s' %(dir_model_name[model_name],branch_name,image_model_name[model_name],sRevision,sDr,image_model_name[model_name]),
                    'cp /tftpboot/build/daily/%s/onie-installer-%s-%s-picos-%s-%s.bin /tftpboot/build/release/%s/%s' %(dir_model_name[model_name],platform,onie_name_map[model_name],branch_name,sRevision,sDr,image_model_name[model_name]),
                    'cd /tftpboot/build/release/%s/%s' %(sDr,image_model_name[model_name]),
                    'md5sum picos-%s-%s-%s.tar.gz >> picos-%s-%s-%s.tar.gz.md5' %(branch_name,image_model_name[model_name],sRevision,branch_name,image_model_name[model_name],sRevision)]
        
        for command in commands:
            api.sendExpect(child=child, command=command)  
            sleep(0.5)


if __name__ == '__main__':
    main(model=['3297','3290'],branch_name='1.1',sRevision='21750',sDr='2.7')
                  
