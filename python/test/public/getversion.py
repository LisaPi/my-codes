#!/usr/bin/env python

import os
import sys
import re
import pexpect

user_name='build'
user_password='build'
prompt='[$#>]'
Type=None

#the image dir model name mapping
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

#image model name mapping
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

def ssh_login(server_ip=None):
    child = pexpect.spawn('ssh %s@%s' % (user_name, server_ip))
    while True:
        i = child.expect(['\$', 'yes/no', 'assword:'])
        if i == 0:
            child.sendline('')
            break 
        elif i ==1:
            child.sendline('yes')  
        else:
            child.sendline('%s' %user_password)

    child.expect(prompt)
    return child


def get_image(server_ip=None, model=None,vtype=None):
    if vtype is None:
        vtype='daily'    
    child = ssh_login(server_ip=server_ip)
    dest_dir = '/tftpboot/build/%s/%s' %(vtype,dir_mode_name[model])
    child.sendline('cd %s' %dest_dir)
    child.expect(prompt)
    child.sendline('ls -lt picos*')
    child.expect('picos-([.0-9]+)-%s-([0-9]+).tar.gz' %image_name[model])
    image = child.match.group()
    print "The latest image is %s" %image
    return image


if __name__ == "__main__":
    get_image (server_ip='10.10.50.16',model='5712',vtype=Type)
    print get_image

                            
