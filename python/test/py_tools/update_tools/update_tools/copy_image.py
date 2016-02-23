#! /usr/bin/env python

Usage = """
Created on 2015-08-31
@author: lisapi
@name: copy_image.py
The script is used to copy images from daily dir to release dir and create md5 file

Usage:

./copy_image.py  sDr,sRevision,branch_name,model

sDr,      the name of release dir name
sRevision,        the revison name
branch_name,      the version name on daiy dir image
model:      the platform name

Example:

./copy_image.py 2.7 22244  1.1 3290
"""

#import some lib
import pexpect
import re
import pxssh
import time
import sys

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
               'HP5712': 'as5712_54x',
               'HP6712': 'as6712_32x',
               'as6712_32x': 'as6712_32x',
               'niagara2948_6xl':'niagara2948_6xl',
               'as4610_54p':'as4610',
               'as4610_30t':'as4610',
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
               'HP5712': 'HP5712',
               'HP6712': 'HP6712',
               'as6712_32x': 'as6712_32x',
               'niagara2948_6xl':'niagara2948_6xl',
               'as4610_54p':'as4610_54p',
               'as4610_30t':'as4610_30t',
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
               'HP5712': 'HP5712',
               'HP6712': 'HP6712',
               'as6712_32x': 'accton_as6712_32x',
               'niagara2948_6xl':'im_niagara2948_6xl',
               'as4610_54p':'accton_as4610_54p',
               'as4610_30t':'accton_as4610_30t',
               'dcs7032q28':'inventec_dcs7032q28',               
               'arctica4804i': 'penguin_arctica4804i'}


user_name= "build"
user_password = 'build'
prompt = '[$#>]'
server_ip = '10.10.50.16'

##Login via ssh
def ssh_login(ip,user,password):
    loginprompt = '[$#>]'
    s = pxssh.pxssh()
    s.login (ip, user, password,original_prompt=loginprompt, login_timeout=1000000)
    return s


##Send and expect 
def sendExpect(child=None, commands=None,exp_prompt=None):

    if exp_prompt is None:
        exp_prompt=prompt 
        
    for command in commands:
            child.sendline ('%s' % command)
            child.expect('(.*)%s' % exp_prompt,timeout=120)
            print "%s%s" %(child.after,child.before)
            
    return child.before, child.after    

    
##Copy image to release dir
def copy_image(sDr=None,sRevision=None,branch_name=None,model=None):

    child = ssh_login(server_ip,user_name,user_password)
    print '******model is %s' %(model)

    for model_name in model:  
        print '***model_name is %s' %(model_name)
        #create dir for release image
        command1 = ['cd  /tftpboot/build/release',
                            'mkdir %s' %sDr,
                            'pwd',
                            'cd %s' %sDr,
                            'mkdir %s' %image_model_name[model_name]]
                            
        sendExpect(child=child, commands=command1,exp_prompt=prompt) 
            
        #copy images to release dir
        if model_name in ['as5712_54x', 'niagara2632xl','niagara2948_6xl','dcs7032q28','HP5712','HP6712','as6712_32x']:
            platform = 'x86'
        elif model_name in ['as4610_54p','as4610_30t']:
            platform = 'arm'
        else:
            platform = 'powerpc'
        print "platform is %s" %platform    
            
        commands = [
                    'cp /tftpboot/build/daily/%s/picos-%s-%s-%s.tar.gz /tftpboot/build/release/%s/%s' % (dir_model_name[model_name],branch_name,image_model_name[model_name],sRevision,sDr,image_model_name[model_name]),
                    'cp /tftpboot/build/daily/%s/pica-switching-%s-%s-%s.deb /tftpboot/build/release/%s/%s' %(dir_model_name[model_name],branch_name,image_model_name[model_name],sRevision,sDr,image_model_name[model_name]),
                    'cp /tftpboot/build/daily/%s/pica-ovs-%s-%s-%s.deb /tftpboot/build/release/%s/%s' % (dir_model_name[model_name],branch_name,image_model_name[model_name],sRevision,sDr,image_model_name[model_name]),
                    'cp /tftpboot/build/daily/%s/pica-linux-%s-%s-%s.deb /tftpboot/build/release/%s/%s' % (dir_model_name[model_name],branch_name,image_model_name[model_name],sRevision,sDr,image_model_name[model_name]),
                    'cp /tftpboot/build/daily/%s/pica-tools-%s-%s-%s.deb /tftpboot/build/release/%s/%s' % (dir_model_name[model_name],branch_name,image_model_name[model_name],sRevision,sDr,image_model_name[model_name]),
                    'cp /tftpboot/build/daily/%s/onie-installer-%s-%s-picos-%s-%s.bin /tftpboot/build/release/%s/%s' % (dir_model_name[model_name],platform,onie_name_map[model_name],branch_name,sRevision,sDr,image_model_name[model_name]),
                    'cd /tftpboot/build/release/%s/%s' %(sDr,image_model_name[model_name]),       
                    'md5sum picos-%s-%s-%s.tar.gz >> picos-%s-%s-%s.tar.gz.md5' % (branch_name,image_model_name[model_name],sRevision,branch_name,image_model_name[model_name],sRevision)]
            
        sendExpect(child=child, commands=commands,exp_prompt=prompt)    


print 'You entered: ', len(sys.argv), 'arguments...'
print 'they are: ', str(sys.argv)

if len(sys.argv) < 5:
    print "\n********You are missing some parameters********\n"
    print Usage
    sys.exit(1)
elif len(sys.argv) == 5:
    sDr,sRevision,branch_name,model = [w for w in sys.argv[1:]]
    model = [s for s in model.split(" ")]
    print '000model:', model
    print '000type(model):', type(model)
    copy_image(sDr=sDr,sRevision=sRevision,branch_name=branch_name,model=model)
    
