#!/usr/bin/env python

"""
Created on 2015-10-20
@author: lisapi
@name: release.py
The script is used to upload images to ftp
"""

#import some lib
import sys
import pexpect
import time
import os
import time


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
               'niagara2948_6xl':'niagara2948_6xl',
               'as4610':'as4610',
               'dcs7032q28':'dcs7032q28',
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
               'niagara2948_6xl':'niagara2948_6xl',
               'as4610':'as4610',
               'dcs7032q28':'dcs7032q28',               
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
               'niagara2632xl': 'im_niagara2632xl',
               'as5712_54x': 'accton_as5712_54x',
               'niagara2948_6xl':'im_niagara2948_6xl',
               'as4610':'accton_as4610',
               'dcs7032q28':'inventec_dcs7032q28',               
               'arctica4804i': 'penguin_arctica4804i'}


host_name = "ftp.pica8.org"
User_name = "engineer@pica8.org"
password = "bj_development?8"
loginprompt = 'ftp>'


##Login ftp server
def ftp_login(host_name=None,User_name=None,password=None):

    child = pexpect.spawn('ftp %s' %(host_name))
    child.expect('Name.*:',timeout=10)
    print child.before,child.after
    child.sendline('%s' %(User_name))
    child.expect('Password:',timeout=10)
    child.sendline('%s' %(password))
    print child.before,child.after
    child.expect(loginprompt,timeout=10)
    child.sendline('cd /')
    print child.before,child.after
    child.expect(loginprompt,timeout=10)
    child.sendline('dir')
    child.expect(loginprompt,timeout=10)
    print child.before,child.after

    return child


##Send and expect 
def send_Expect(child=None, commands=None):

    prompt = 'ftp>'    
    for command in commands:
            child.sendline ('%s' % command)
            child.expect('(.*)%s' % prompt,timeout=180)
            print "%s%s" %(child.after,child.before)
            
    return child.before, child.after    


def upload_image(sDr=None,sRevision=None,branch_name=None,model_name=None):
    
    print '***model_name is %s' %(model_name)   
    #enter image dir    
    child = ftp_login(host_name=host_name,User_name=User_name,password=password)                  
    if model_name in ['as5712_54x', 'niagara2632xl','niagara2948_6xl','dcs7032q28']:
        platform = 'x86'
    elif model_name in ['as4610']:  
        platform = 'arm'
    else:
        platform = 'powerpc'  
    print '@@@platform is %s' %(platform) 

    #create dir for release image        
    command1 = ['dir',               
                'mkdir release-%s' %sDr,              
                'chmod 777 release-%s' %sDr,
                'cd release-%s' %sDr,
                'bin',
                'put  picos-%s-%s-%s.tar.gz'  %(branch_name,image_model_name[model_name],sRevision),
                'put onie-installer-%s-%s-picos-%s-%s.bin' %(platform,onie_name_map[model_name],branch_name,sRevision)]
                     
    send_Expect (child=child, commands=command1)                                  
    print '####### create release-dir and uplaod ######'
        


     
if __name__ == "__main__":
     upload_image(sDr='2.6.3',sRevision=23617,branch_name='2.6.3',model_name='5401')   
