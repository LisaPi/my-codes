#! /usr/bin/env python

Usage = """
Created on 2015-07-01
@author: lisapi
@name: buildimage.py

The script is used to build images for pica8,
supporting branches: 1.1  2.6 verizon 2.6B netconf
supporting models:3290 3295 3297 3922 3924 3930 3780 5401 es4654bf as6701_32x as5712_54x niagara2632xl arctica4804i niagara2948_6xl HP5712 as4610_54 dcs7032q28

Usage:

./build.py branch_name server_ip model_name  is_license  is_sdk depend_version

branch_name,      the name of branch (eg, 1.1)
server_ip,        the server of code (eg. 10.10.50.16)
model_name,       the name of model (eg. 3290)
is_license:       the image is licensed (0: no-license, 1: has-license)
is_sdk:            the image is sdked(0:no make sdk,1:make sdk)

Example:

./buildimage.py 1.1 10.10.50.16 3290 1 0

"""

# import common lib
import pexpect
import sys
import string
import re
import os
from smtplib import SMTP
from poplib import POP3
from time import sleep

SMTPSVR = '10.10.50.11'
branch_id = ['1.1','2.6','verizon','2.6B','netconfig']
model_type = ['3290', '3295', '3297', '3920', '3922', '3924', '3930', '3780', '5401', '5101', 'es4654bf', 'as6701_32x', 'as5712_54x', 'niagara2632xl', 'arctica4804i','niagara2948_6xl', 'HP5712', 'as4610_54', 'dcs7032q28']

# Build specific pica xorplus mapping
pica_xorp_map = {'1.1': 'xorplus',
                 '2.6': 'pica',
                 '2.6B': 'xorplus',
                 'netconfig': 'xorplus',
                 'verizon': 'xorplus'}
         
# Build platform sdk mapping 
sdk_dict = {'3290': 'sdk-xgs-robo-6.3.2',
               '3295': 'sdk-xgs-robo-6.3.2',
               '3297': 'sdk-xgs-robo-6.3.2',
               '3922': 'sdk-xgs-robo-6.3.2',
               '3920': 'sdk-xgs-robo-6.3.2',
               '3924': 'sdk-xgs-robo-6.3.2',
               '3930': 'sdk-xgs-robo-6.3.2',
               '3780': 'sdk-xgs-robo-6.3.2',
               '5101': 'sdk-xgs-robo-6.3.2',
               '5401': 'sdk-xgs-robo-6.3.2',
               'es4654bf': 'sdk-xgs-robo-6.3.2',
               'as6701_32x': 'sdk-xgs-robo-6.3.2',
               'niagara2632xl': 'sdk-xgs-robo-6.3.9',
               'niagara2948_6xl': 'sdk-xgs-robo-6.3.9',
               'as5712_54x': 'sdk-xgs-robo-6.3.9',
               'HP5712': 'sdk-xgs-robo-6.3.9',
               'as4610_54':'sdk-xgs-robo-6.4.5',
               'dcs7032q28':'sdk-xgs-robo-6.4.5',
               'arctica4804i': 'sdk-xgs-robo-6.3.2'}

# Build specific sdk id mapping
sdk_id_map = {'1.1': '',
                      '2.6': '',
                      '2.6B': '',
                      'netconfig':'',
                      'verizon': '' }    
          
# Build platform kernel mapping     
kernel_dict = {'3290': 'linux-2.6.27-lb9a',
                   '3295': 'linux-2.6.27-lb9a',
                   '3297': 'linux-2.6.32-pronto3296',
                   '3922': 'linux-2.6.32.13-pronto3922',
                   '3920': 'linux-2.6.32.24-lb8d',
                   '3924': 'linux-3.4.82',
                   '3930': 'linux-2.6.32.24-lb8d',
                   '3780': 'linux-2.6.27-lb9a',
                   '5101': 'linux-3.4.82',
                   '5401': 'linux-3.0.48-pronto5401',
                   'es4654bf': 'linux-3.4.82',
                   'as6701_32x': 'linux-3.4.82',
                   'niagara2632xl': 'linux-3.4.82-x86_64',
                   'niagara2948_6xl': 'linux-3.4.82-x86_64',
                   'as5712_54x': 'linux-3.4.82-x86_64',
                   'HP5712': 'linux-3.4.82-x86_64',
                   'as4610_54':'linux-3.6.5-accton',
                   'dcs7032q28':'linux-3.2.35-inventec',
                   'arctica4804i': 'linux-3.2.35-onie'}
       
# Build platform  powerpcspe mapping 
ppc_dict  = {'1.1': 'rootfs-debian-basic',
               '2.6': 'rootfs-debian-basic',
               '2.6B': 'rootfs-debian-basic',
               'netconfig': 'rootfs-debian-basic',
               'verizon': 'rootfs-debian-basic'}
               

# Build box dir name mapping under os
box_name_map = {'3290': 'pronto3290',
               '3295': 'pronto3295',
               '3297': 'pronto3296',
               '3922': 'pronto3922',
               '3920': 'pronto3920',
               '3924': 'pronto3924',
               '3930': 'pronto3930',
               '3780': 'pronto3780',
               '5101': 'pronto5101',
               '5401': 'pronto5401',
               'es4654bf': 'es4654bf',
               'as6701_32x': 'as6701_32x',
               'niagara2632xl': 'niagara2632xl',
               'niagara2948_6xl': 'niagara2948-6xl',
               'as5712_54x': 'as5712_54x',
               'HP5712': 'as5712_54x',
               'as4610_54':'as4610_54p',
               'dcs7032q28':'dcs7032q28',
               'arctica4804i': 'arctica4804i'}


#Build box dir name for make mapping
box_map = {'3290': 'p3290',
               '3295': 'p3295',
               '3297': 'p3296',
               '3922': 'p3922',
               '3920': 'p3920',
               '3924': 'p3924',
               '3930': 'p3930',
               '3780': 'p3780',
               '5101': 'p5101',
               '5401': 'p5401',
               'es4654bf': 'es4654bf',
               'as6701_32x': 'as6701_32x',
               'niagara2632xl': 'niagara2632xl',
               'niagara2948_6xl': 'niagara2948-6xl',
               'as5712_54x': 'as5712_54x',
               'HP5712': 'as5712_54x',
               'as4610_54':'as4610_54p',
               'dcs7032q28':'dcs7032q28',
               'arctica4804i': 'arctica4804i'}

#Image dir name mapping
model_dir_name = {'3290': '3290',
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
               'niagara2948_6xl': 'niagara2948_6xl',
               'as5712_54x': 'as5712_54x',
               'HP5712': 'as5712_54x',
               'as4610_54':'as4610_54p',
               'dcs7032q28':'dcs7032q28',
               'arctica4804i': 'arctica4804i'}
   
# Build os directory mapping
os_name_map = {'1.1': 'os-dev',
               '2.6': 'os-dev',
               '2.6B': 'os-dev',
               'netconfig': 'os-dev',
               'verizon': 'os-dev'}
               

# Build relative directory mapping
rel_name_map = {'1.1': '.',
               '2.6': '.',
               '2.6B': '.',
               'netconfig': '.',
               'verizon': '.'}
               

# Build cross compile mapping
cross_compile_map = {'3290': 'powerpc-linux',
                    '3295': 'powerpc-linux',
                    '3297': 'powerpc-linux-gnuspe',
                    '3922': 'powerpc-linux-gnuspe',
                    '3920': 'powerpc-linux-gnuspe',
                    '3924': 'powerpc-linux-gnuspe',
                    '3930': 'powerpc-linux-gnuspe',
                    '3780': 'powerpc-linux-gnuspe',
                    '5101': 'powerpc-linux-gnuspe',
                    '5401': 'powerpc-linux-gnuspe',
                    'es4654bf': 'powerpc-linux-gnuspe',
                    'as6701_32x': 'powerpc-linux-gnuspe',
                    'niagara2632xl': '',
                    'niagara2948_6xl': '',
                    'as5712_54x': '',
                    'HP5712': '',
                    'as4610_54':'arm-linux-gnueabi',
                    'dcs7032q28':'',
                    'arctica4804i': 'powerpc-linux-gnuspe'}
               
# Build ovs model name mapping 
ovs_model_map = {'3290': '3290new',
                    '3295': '3295new',
                    '3297': '3296new',
                    '3922': '3922new',
                    '3920': '3920new',
                    '3924': '3924',
                    '3930': '3930',
                    '3780': '3780new',
                    '5101': '5101',
                    '5401': '5401',
                    'es4654bf': 'es4654bf',
                    'as6701_32x': 'as6701_32x',
                    'niagara2632xl': 'niagara2632xl',
                    'niagara2948_6xl': 'niagara2948_6xl',
                    'as5712_54x': 'as5712_54x',
                    'HP5712': 'as5712_54x',
                    'as4610_54':'as4610_54p',
                    'dcs7032q28':'dcs7032q28',
                    'arctica4804i': 'arctica4804i'}
                    
                                   
# User info
user_name = 'build'
user_password = 'build'
prompt = '[$#>]'

# Build pica config name
pica_config_name = {}
for branch in branch_id:
    pica_config_name.setdefault(branch, {})
    for model in model_type:
        if model in ['as5712_54x', 'niagara2632xl', 'niagara2948_6xl','HP5712']:
            sDirs = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model).group(), branch)
            hTmp = rel_name_map[branch]
            oDir = os_name_map[branch]
            hType = cross_compile_map[model]
            sNoDug = '--disable-debug'
            sOpt = '--enable-optimize'
            sBox = model
            sLib =  sdk_dict[model] 
            sBcm = 'bcm_%s' %(re.search("([.0-9]+)", sLib).group())         
            pica_config_name[branch][model] = './configure --prefix=%s/%s/%s/%s/rootfs-debian/%s \
                                          --host=%s \
                                          --enable-static=no %s %s \
                                          --with-%s \
                                          --with-lcmgr=yes \
                                        --with-rootfs_debian=yes \
                                        ovs_cv_use_linker_sections=yes \
                                        --with-sdk_6_3_9=yes  \
                                        --with-chip_sdk_lib_path=%s/pica/exlib/%s.%s \
                                        --with-chip_sdk_deprecated_version=no \
                                        --with-chip_sdk_root_path=%s/%s/sdk/%s \
                                        ' % (sDirs, hTmp, oDir, box_name_map[model], pica_xorp_map[branch], hType, sNoDug, sOpt, model_dir_name[model], sDirs, sBcm, box_map[model], sDirs, hTmp, sLib)     
        elif model in ['as4610_54','dcs7032q28']:
            sDirs = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model).group(), branch)
            hTmp = rel_name_map[branch]
            oDir = os_name_map[branch]
            hType = cross_compile_map[model]
            sNoDug = '--disable-debug'
            sOpt = '--enable-optimize'
            sBox = model
            sLib =  sdk_dict[model] 
            sBcm = 'bcm_%s' %(re.search("([.0-9]+)", sLib).group())         
            pica_config_name[branch][model] = './configure --prefix=%s/%s/%s/%s/rootfs-debian/%s \
                                          --host=%s \
                                          --enable-static=no %s %s \
                                          --with-%s \
                                          --with-lcmgr=yes \
                                        --with-rootfs_debian=yes \
                                        ovs_cv_use_linker_sections=yes \
                                        --with-sdk_6_4_5=yes  \
                                        --with-chip_sdk_lib_path=%s/pica/exlib/%s.%s \
                                        --with-chip_sdk_deprecated_version=no \
                                        --with-chip_sdk_root_path=%s/%s/sdk/%s \
                                        ' % (sDirs, hTmp, oDir, box_name_map[model], pica_xorp_map[branch], hType, sNoDug, sOpt, model_dir_name[model], sDirs, sBcm, box_map[model], sDirs, hTmp, sLib)    
        elif model in ['dcs7032q28']:
            sDirs = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model).group(), branch)
            hTmp = rel_name_map[branch]
            oDir = os_name_map[branch]
            hType = cross_compile_map[model]
            sNoDug = '--disable-debug'
            sOpt = '--enable-optimize'
            sBox = model
            sLib =  sdk_dict[model] 
            sBcm = 'bcm_%s' %(re.search("([.0-9]+)", sLib).group())         
            pica_config_name[branch][model] = './configure --prefix=%s/%s/%s/%s/rootfs-debian/%s \
                                          --host=%s \
                                          --enable-static=no %s %s \
                                          --with-%s \
                                          --with-lcmgr=yes \
                                        --with-rootfs_debian=yes \
                                        ovs_cv_use_linker_sections=yes \
                                        --with-sdk_6_4_7=yes  \
                                        --with-chip_sdk_lib_path=%s/pica/exlib/%s.%s \
                                        --with-chip_sdk_deprecated_version=no \
                                        --with-chip_sdk_root_path=%s/%s/sdk/%s \
                                        ' % (sDirs, hTmp, oDir, box_name_map[model], pica_xorp_map[branch], hType, sNoDug, sOpt, model_dir_name[model], sDirs, sBcm, box_map[model], sDirs, hTmp, sLib)                                                  
        elif model in ['arctica4804i']:
            sDirs = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model).group(), branch)
            hTmp = rel_name_map[branch]
            oDir = os_name_map[branch]
            hType = cross_compile_map[model]
            sNoDug = '--disable-debug'
            sOpt = '--enable-optimize'
            sBox = model
            sLib =  sdk_dict[model]
            sBcm = 'bcm_%s' %(re.search("([.0-9]+)", sLib).group())
            pica_config_name[branch][model] = './configure --prefix=%s/%s/%s/%s/rootfs-debian/%s \
                                          --host=%s \
                                          --enable-static=no %s %s \
                                          --with-pronto%s \
                                          --with-lcmgr=yes \
                                        --with-rootfs_debian=yes \
                                        ovs_cv_use_linker_sections=yes \
                                        --with-chip_sdk_lib_path=%s/pica/exlib/%s.%s \
                                        --with-chip_sdk_deprecated_version=no \
                                        --with-chip_sdk_root_path=%s/%s/sdk/%s \
                                        ' % (sDirs, hTmp, oDir, box_name_map[model], pica_xorp_map[branch], hType, sNoDug, sOpt, '3296' ,sDirs, sBcm, box_map[model], sDirs, hTmp, sLib)
        else:
            sDirs = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model).group(), branch)
            hTmp = rel_name_map[branch]
            oDir = os_name_map[branch]
            hType = cross_compile_map[model]
            sNoDug = '--disable-debug'
            sOpt = '--enable-optimize'
            sBox = model
            sLib =  sdk_dict[model]
            sBcm = 'bcm_%s' %(re.search("([.0-9]+)", sLib).group() )                
            pica_config_name[branch][model] = './configure --prefix=%s/%s/%s/%s/rootfs-debian/%s \
                                          --host=%s \
                                          --enable-static=no %s %s \
                                          --with-%s \
                                          --with-lcmgr=yes \
                                        --with-rootfs_debian=yes \
                                        ovs_cv_use_linker_sections=yes \
                                        --with-chip_sdk_lib_path=%s/pica/exlib/%s.%s \
                                        --with-chip_sdk_deprecated_version=no \
                                        --with-chip_sdk_root_path=%s/%s/sdk/%s \
                                        ' % (sDirs, hTmp, oDir, box_name_map[model], pica_xorp_map[branch], hType, sNoDug, sOpt, box_name_map[model], sDirs, sBcm, box_map[model], sDirs, hTmp, sLib)               

# Build ovs config name 
ovs_config_name = {}
for branch in branch_id:
    ovs_config_name.setdefault(branch, {})
    for model in model_type:
        if model in ['as5712_54x', 'es4654bf', 'as6701_32x', 'niagara2632xl', 'niagara2948_6xl','HP5712','as4610_54','dcs7032q28']:
            hType = cross_compile_map[model]
            pBox = ovs_model_map[model]
            ovs_config_name[branch][model] = './configure --host=%s --with-%s -with-switchdir=/ovs \
                                               ' % (hType, pBox)                                              
        elif model in ['arctica4804i']:
            hType = cross_compile_map[model]
            pBox = '%s%s' % ('3296','new')
            ovs_config_name[branch][model] = './configure --host=%s --with-pronto%s -with-switchdir=/ovs \
                                               ' % (hType, pBox)
        else:
            hType = cross_compile_map[model]
            pBox = ovs_model_map[model]
            ovs_config_name[branch][model] = './configure --host=%s --with-pronto%s -with-switchdir=/ovs \
                                               ' % (hType, pBox)
                          

# Build onie map
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
               'niagara2948_6xl': 'im_niagara2948_6xl',
               'as5712_54x': 'accton_as5712_54x',
               'HP5712': 'HP5712',
               'as4610_54':'accton_as4610_54',
               'dcs7032q28':'inventec_dcs7032q28',
               'arctica4804i': 'penguin_arctica4804i'}

# Build image model name
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
               'niagara2948_6xl': 'niagara2948_6xl',
               'as5712_54x': 'as5712_54x',
               'HP5712': 'HP5712',
               'as4610_54':'as4610_54',
               'dcs7032q28':'dcs7032q28',
               'arctica4804i': 'arctica4804i'}

# Build image directory name
image_dir_name = {'3290': '/tftpboot/%s/daily/3290' % user_name,
               '3295': '/tftpboot/%s/daily/3295' % user_name,
               '3297': '/tftpboot/%s/daily/3297' % user_name,
               '3922': '/tftpboot/%s/daily/3922' % user_name,
               '3920': '/tftpboot/%s/daily/3920' % user_name,
               '3924': '/tftpboot/%s/daily/as5600_52x' % user_name,
               '3930': '/tftpboot/%s/daily/3930' % user_name,
               '3780': '/tftpboot/%s/daily/3780' % user_name,
               '5101': '/tftpboot/%s/daily/5101' % user_name,
               '5401': '/tftpboot/%s/daily/5401' % user_name,
               'es4654bf': '/tftpboot/%s/daily/as4600_54t' % user_name,
               'as6701_32x': '/tftpboot/%s/daily/as6701_32x' % user_name,
               'niagara2632xl': '/tftpboot/%s/daily/niagara2632xl' % user_name,
               'niagara2948_6xl': '/tftpboot/%s/daily/niagara2948_6xl' % user_name,
               'as5712_54x': '/tftpboot/%s/daily/as5712_54x' % user_name,
               'HP5712': '/tftpboot/%s/daily/as5712_54x' % user_name,
               'as4610_54':'/tftpboot/%s/daily/as4610_54p' % user_name,
               'dcs7032q28':'/tftpboot/%s/daily/dcs7032q28' % user_name,
               'arctica4804i': '/tftpboot/%s/daily/arctica4804i' % user_name}

######define functions for build image
######Send email
def execute_send_email(err_subject=None, err_buffer=None, current_version=None, branch_name=None):
    
    who = 'build@pica8.local'
    whos = "lpi@pica8.local"

    origBody = '''\
From: %(who)s
To: %(whos)s
Subject: %(subject)s

%(err_buffer)s

Version:%(current_version)s
Branch:%(branch_name)s
''' % {'who': who, 'whos':whos, 'subject': err_subject, 
       'err_buffer': err_buffer, 'current_version': current_version,
       'branch_name': branch_name}

    sendSvr = SMTP(SMTPSVR)
    errs = sendSvr.sendmail(who, [whos], origBody)
    sendSvr.quit()
    assert len(errs) == 0, errs
    sleep(10)
                       

######  Login server
def server_ssh_login(server_ip=None):
    
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

###### Execute send and expect
def execute_send_expect(child=None, commands=None, exp_prompt=None, err_subject=None, current_version=None, branch_name=None):
    
    if exp_prompt is None:
        exp_prompt = prompt
        
    for command in commands:
        if command == 'make -j8':
            child.sendline ('%s' % command)
            i = child.expect(['([\s\S]{100}Error )', '%s@.*%s' % (user_name, exp_prompt)], timeout=None)
            if i == 0:
                err_buffer = child.match.group(1)
                execute_send_email(err_subject=err_subject, err_buffer=err_buffer, 
                                  current_version=current_version, branch_name=branch_name,
                                      )
                sys.exit()
        else:   
            if re.search('scp|rm', command):
                child.sendline ('%s' % command)
                while True:
                    i = child.expect(['\$', 'yes/no', 'assword:|password for'], timeout=None)
                    if i == 0:
                        child.sendline('')
                        child.expect(prompt)
                        break
                    elif i == 1:
                        child.sendlist('yes')
                    else:
                        child.sendline('%s' % user_password)
            else:
                child.sendline ('%s' % command)
                child.expect(pattern='%s@.*%s' % (user_name, exp_prompt), timeout=None)
   
###### Svn Cleanup/Update
def execute_svn_update(server_ip=None, branch_name=None, model_name=None):

    # Get id
    child = server_ssh_login(server_ip=server_ip)
    
    # Codes directory
    dest_dir = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model_name).group(), branch_name)
    execute_send_expect(child=child, commands=['cd %s' % dest_dir])
    
    # SVN update
    execute_send_expect(child=child, commands=['rm -rf %s/sdk/%s' % (rel_name_map[branch_name],sdk_dict[model_name])])
    execute_send_expect(child=child, commands=['svn update %s %s/sdk/%s' % (sdk_id_map[branch_name],rel_name_map[branch_name], sdk_dict[model_name])])

    # Branch update
    if svn_type == 0:
        commands = [
                    'sudo rm -rf *', 
                    'sudo rm -rf %s/%s/%s' % (rel_name_map[branch_name], os_name_map[branch_name], box_name_map[model_name]), 
                    'sudo rm -rf %s/%s/%s' % (rel_name_map[branch_name], os_name_map[branch_name], ppc_dict[branch_name]),
                    'sudo rm -rf %s/%s/%s' % (rel_name_map[branch_name], os_name_map[branch_name], kernel_dict[model_name]),
                    'svn up %s/%s/%s' % (rel_name_map[branch_name], os_name_map[branch_name], box_name_map[model_name]), 
                    'svn up %s/%s/%s' % (rel_name_map[branch_name], os_name_map[branch_name], ppc_dict[branch_name]),
                    'svn up %s/%s/%s' % (rel_name_map[branch_name], os_name_map[branch_name], kernel_dict[model_name]),
                    'svn up',
                    'ls | grep -v os-dev | grep -v sdk | xargs chown -R %s' % user_name,
                    'ls | grep -v os-dev | grep -v sdk | xargs chgrp -R %s' % user_name]
        execute_send_expect(child=child, commands=commands)   
                               
    elif svn_type == 1:
        commands = [ 
                    'svn up %s/%s/%s' % (rel_name_map[branch_name], os_name_map[branch_name], box_name_map[model_name]), 
                    'svn up %s/%s/%s' % (rel_name_map[branch_name], os_name_map[branch_name], ppc_dict[branch_name]),
                    'svn up %s/%s/%s' % (rel_name_map[branch_name], os_name_map[branch_name], kernel_dict[model_name]),
                    'svn up',
                    'ls | grep -v os-dev | grep -v sdk | xargs chown -R %s' % user_name,
                    'ls | grep -v os-dev | grep -v sdk | xargs chgrp -R %s' % user_name]
        execute_send_expect(child=child, commands=commands)   
                               
    else:
        commands = [ 
                'ls | grep -v os-dev | grep -v sdk | xargs chown -R %s' % user_name,
                'ls | grep -v os-dev | grep -v sdk | xargs chgrp -R %s' % user_name]    
        execute_send_expect(child=child, commands=commands)
    

###### Get the version Id number
def get_id_number(server_ip=None, branch_name=None, model_name=None):                    

    # Get id
    child = server_ssh_login(server_ip=server_ip)

    # Codes directory
    dest_dir = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model_name).group(), branch_name)
    execute_send_expect(child=child, commands=['cd %s' % dest_dir])
    child.sendline('grep support@pica8.org configure.ac')
    child.expect('pica,\s+\[([0-9a-zA-Z.]+)\]')
    id_num = child.match.group(1)

    if branch_name in ['1.1']:
        id_num = '1.1'

    return id_num


###### Get the reversion number
def get_version_number(server_ip=None, branch_name=None, model_name=None):                    

    # Get id
    child = server_ssh_login(server_ip=server_ip)
    
    # Codes directory
    dest_dir = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model_name).group(), branch_name)
    execute_send_expect(child=child, commands=['cd %s' % dest_dir])
    
    child.sendline('svn info')
    child.expect('Last Changed Rev:\s+([0-9]+)')
    version = child.match.group(1)
    
    return version

        
###### Pica build 
def execute_pica_make(server_ip=None, branch_name=None, model_name=None,
                     is_license=None, brand_name=None, company_name=None,
                     platform_name=None, host_name=None,
                     current_version=None, reversion_id=None):

    # Get id
    child = server_ssh_login(server_ip=server_ip)
    
    # Codes directory
    dest_dir = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model_name).group(), branch_name)
    execute_send_expect(child=child, commands=['cd %s' % dest_dir])
    
    # Make
    sDirs = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model_name).group(), branch_name)
    hTmp = rel_name_map[branch_name]
    oDir = os_name_map[branch_name]
    commands = [
                'export CROSS_COMPILE=%s-' % cross_compile_map[model_name],
                './bootstrap',
                '%s %s --with-brand-name=%s --with-company-name=%s --with-platform-name=%s --with-host-name=%s' % (pica_config_name[branch_name][model_name], is_license, brand_name, company_name, platform_name, host_name),
                'make -j8',
                'make install',
                'cd %s/%s/%s/%s/rootfs-debian/%s' % (sDirs,hTmp,oDir,box_name_map[model_name],pica_xorp_map[branch_name]),
                'tar -czvf /tftpboot/%s/daily/%s/pica_bin-%s-%s-%s.tar.gz bin/*' % (user_name, model_dir_name[model_name], reversion_id, image_model_name[model_name], current_version),
                'cd %s' % dest_dir,
                'make install-strip'
                ]
    execute_send_expect(child=child, commands=commands, err_subject='%s Pica make error!' % model_name, current_version=current_version, branch_name=branch_name)

        
###### Ovs build
def execute_ovs_make(server_ip=None, branch_name=None, 
                    model_name=None, is_license=None, sbrand_name=None,
                    current_version=None, reversion_id=None):

    # Get  id
    child = server_ssh_login(server_ip=server_ip)
    
    # Codes directory
    ovs_version = 'openvswitch-2.3.0'
    dest_dir = '/home/%s/%s/release/pica8/branches/%s/ovs/%s' % (user_name, re.search("([0-9]{4})", model_name).group(), branch_name, ovs_version)
    execute_send_expect(child=child, commands=['cd %s' % dest_dir])
   
    # Make
    sDirs = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model_name).group(), branch_name)
    hTmp = rel_name_map[branch_name]
    oDir = os_name_map[branch_name]
    commands = [
                'export CROSS_COMPILE=%s-' % cross_compile_map[model_name],
                'autoreconf --install --force',
                '%s %s --prefix=%s/%s/%s/%s/rootfs-debian/ovs --with-brand-name=%s' % (ovs_config_name[branch_name][model_name], is_license, sDirs, hTmp, oDir, box_name_map[model_name], sbrand_name),
                'make -j8',
                'make install',
                'make install-strip',
                'make install-xlib-strip',
                'tar -czvf /tftpboot/%s/daily/%s/ovs_bin-%s-%s-%s.tar.gz ./vswitchd/ovs-vswitchd.dbg ./ovsdb/ovsdb-server.dbg ./utilities/ovs-appctl.dbg ./utilities/ovs-vsctl.dbg ./utilities/ovs-ofctl.dbg' % (user_name, model_dir_name[model_name], reversion_id, image_model_name[model_name], current_version)
                ]
    execute_send_expect(child=child, commands=commands, err_subject='%s Ovs %s make error!' % (model_name, ovs_version), current_version=current_version, branch_name=branch_name)


###### Oms build
def execute_oms_make(server_ip=None, branch_name=None, model_name=None):

    # Get  id
    child = server_ssh_login(server_ip=server_ip)
    
    # Codes directory
    dest_dir = '/home/%s/%s/release/pica8/branches/%s/ovs/oms' % (user_name, re.search("([0-9]{4})", model_name).group(), branch_name)
    execute_send_expect(child=child, commands=['cd %s' % dest_dir])
   
    # Make
    sDirs = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model_name).group(), branch_name)
    hTmp = rel_name_map[branch_name]
    oDir = os_name_map[branch_name] 
    execute_send_expect(child=child, commands=['python build.py %s %s/%s/%s v2.0' % (box_name_map[model], sDirs, hTmp, oDir)])
      
   
###### Os-dev build
def execute_os_make(server_ip=None, branch_name=None, 
                   model_name=None, current_version=None, 
                   depend_version=None, reversion_id=None):

    # Get  id
    child = server_ssh_login(server_ip=server_ip)   
    sDirs = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model_name).group(), branch_name)
    hTmp = rel_name_map[branch_name]
    oDir = os_name_map[branch_name]
    sLib =  sdk_dict[model_name]   
    
    # Codes directory
    dest_dir = '%s/%s/%s/%s' % (sDirs, hTmp, oDir, box_name_map[model_name])
    execute_send_expect(child=child, commands=['cd %s' % dest_dir])
   
    # Make
    commands = [
              'export CROSS_COMPILE=%s-' % cross_compile_map[model_name],
              'export CROSS_COMPILE_PATH=/tools/eldk4.2/usr/',
              'export PATH=$CROSS_COMPILE_PATH/bin:$PATH',
               ]
    execute_send_expect(child=child, commands=commands)
    
    if model_name not in ['as5712_54x', 'niagara2632xl','niagara2948_6xl','HP5712','dcs7032q28']:
        commands = [
                'export ARCH=powerpc',
                ]
        execute_send_expect(child=child, commands=commands) 
        
    # make 
    sVersion = current_version
    if depend_version is None:
        sDepend = sVersion
    else:
        sDepend = depend_version
    rId = reversion_id
    sRevison =  " REVISION_NUM=%s RELEASE_VER=%s \
                      LINUX_DEB_VERSION=%s-%s \
                      TOOLS_DEB_VERSION=%s-%s \
                      XORP_LINUX_DEB_DEPEND_VERSION=%s-%s \
                      OVS_LINUX_DEB_DEPEND_VERSION=%s-%s \
                      XORP_TOOLS_DEB_DEPEND_VERSION=%s-%s \
                      OVS_TOOLS_DEB_DEPEND_VERSION=%s-%s"  % (sVersion, rId, rId, 
                                                              sDepend, rId, sDepend,
                                                              rId, sDepend, rId, sDepend,
                                                              rId, sDepend, rId, sDepend)

       
    if model_name in ['as5712_54x', 'niagara2632xl', 'niagara2948_6xl','as4610_54','dcs7032q28']:
        lBox = string.upper(box_name_map[model_name])
        commands = [
                'sudo make fast PICA8=1 %s=1 SDK=%s/%s/sdk/%s BRANCH=%s%s' % (lBox, sDirs, hTmp,
                                                                              sLib,branch_name,sRevison)
                ]               
    elif model_name in ['HP5712']:
        commands = [
                'sudo make fast PICA8=1 %s=1 SDK=%s/%s/sdk/%s BRANCH=%s%s' % ('HP5712', sDirs, hTmp,
                                                                              sLib,branch_name,sRevison)
                ]           
    else:
        lBox = string.upper(box_name_map[model_name])
        commands = [
                'sudo make fast %s=1 SDK=%s/%s/sdk/%s BRANCH=%s%s' % (lBox, sDirs, hTmp, sLib,branch_name,sRevison)  
                    ]      
    execute_send_expect(child=child, commands=commands)   

###### SDK build
def execute_sdk_make(server_ip=None, branch_name=None, 
                   model_name=None, current_version=None, 
                   depend_version=None, reversion_id=None):

    # Get  id
    child = server_ssh_login(server_ip=server_ip)   
    sDirs = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model_name).group(), branch_name)
    hTmp = rel_name_map[branch_name]
    oDir = os_name_map[branch_name]
    sLib =  sdk_dict[model_name]
   
    # Codes directory
    dest_dir = '%s/%s/%s/%s' % (sDirs, hTmp, oDir, box_name_map[model_name])
    execute_send_expect(child=child, commands=['cd %s' % dest_dir])
   
    # Make
    commands = [
              'export CROSS_COMPILE=%s-' % cross_compile_map[model_name],
              'export CROSS_COMPILE_PATH=/tools/eldk4.2/usr/',
              'export PATH=$CROSS_COMPILE_PATH/bin:$PATH',
               ]
    execute_send_expect(child=child, commands=commands)
    
    if model_name not in ['as5712_54x', 'niagara2632xl','niagara2948_6xl','HP5712','dcs7032q28']:
        commands = [
                'export ARCH=powerpc',
                ]
        execute_send_expect(child=child, commands=commands) 
        
    # make sdk  
    sVersion = current_version
    if depend_version is None:
        sDepend = sVersion
    else:
        sDepend = depend_version
    rId = reversion_id
    sRevison =  " REVISION_NUM=%s RELEASE_VER=%s \
                      LINUX_DEB_VERSION=%s-%s \
                      TOOLS_DEB_VERSION=%s-%s \
                      XORP_LINUX_DEB_DEPEND_VERSION=%s-%s \
                      OVS_LINUX_DEB_DEPEND_VERSION=%s-%s \
                      XORP_TOOLS_DEB_DEPEND_VERSION=%s-%s \
                      OVS_TOOLS_DEB_DEPEND_VERSION=%s-%s"  % (sVersion, rId, rId, 
                                                              sDepend, rId, sDepend,
                                                              rId, sDepend, rId, sDepend,
                                                              rId, sDepend, rId, sDepend)

       
    if model_name in ['as5712_54x', 'niagara2632xl', 'niagara2948_6xl','as4610_54','dcs7032q28']:
        lBox = string.upper(box_name_map[model_name])
        commands = [
                'sudo make BCM_SDK_ALL  PICA8=1 %s=1 SDK=%s/%s/sdk/%s BRANCH=%s%s' % (lBox, sDirs, hTmp,
                                                                              sLib,branch_name,sRevison)
                ]
    elif  model_name in ['HP5712']:
        commands = [
                'sudo make BCM_SDK_ALL  PICA8=1 %s=1 SDK=%s/%s/sdk/%s BRANCH=%s%s' % ('HP5712', sDirs, hTmp,
                                                                              sLib,branch_name,sRevison)
                ]        
    else:
        lBox = string.upper(box_name_map[model_name])
        commands = [
                'sudo make BCM_SDK_ALL %s=1 SDK=%s/%s/sdk/%s BRANCH=%s%s' % (lBox, sDirs, hTmp, sLib,branch_name,sRevison)  
                    ]      
    execute_send_expect(child=child, commands=commands)   
    
###### Copy the build images
def execute_image_copy(server_ip=None, branch_name=None, model_name=None, reversion_id=None, version_number=None):
    
    # Get  id
    child = server_ssh_login(server_ip=server_ip)
    
    sDirs = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model_name).group(), branch_name)
    hTmp = rel_name_map[branch_name]
    oDir = os_name_map[branch_name]
                
    # Codes directory
    dest_dir = '%s/%s/%s/%s' % (sDirs, hTmp, oDir, box_name_map[model_name])
    execute_send_expect(child=child, commands=['cd %s' % dest_dir])
    
    # Do the copy
    if model_name in ['as5712_54x', 'niagara2632xl','niagara2948_6xl','dcs7032q28']:
        onie_platform = 'x86'
        copyCmd = 'scp'
        dirIp = '%s@10.10.50.16:' % user_name
        commands = ['%s build_image/%s.tar.gz %s%s/pica-%s-%s-%s.tar.gz' % (copyCmd, 
                                                                               pica_xorp_map[branch_name],
                                                                               dirIp,
                                                                               image_dir_name[model_name],
                                                                               reversion_id,
                                                                               image_model_name[model_name],
                                                                               version_number),
                    '%s build_image/rootfs.tar.gz %s%s/picos-%s-%s-%s.tar.gz' % (copyCmd,
                                                                                  dirIp,
                                                                                  image_dir_name[model_name],
                                                                                  reversion_id,
                                                                                  image_model_name[model_name],
                                                                                  version_number),
                    '%s build_image/picos_onie_installer.bin %s%s/onie-installer-%s-%s-picos-%s-%s.bin' % (copyCmd,
                                                                                                   dirIp,
                                                                                                   image_dir_name[model_name],
                                                                                                   onie_platform,
                                                                                                   onie_name_map[model_name],
                                                                                                   reversion_id,
                                                                                                   version_number),
                    '%s build_image/ovs.deb %s%s/pica-ovs-%s-%s-%s.deb' % (copyCmd,
                                                                            dirIp,
                                                                            image_dir_name[model_name],
                                                                            reversion_id,
                                                                            image_model_name[model_name],
                                                                            version_number),
                    '%s build_image/xorp.deb %s%s/pica-switching-%s-%s-%s.deb' % (copyCmd,
                                                                                   dirIp,
                                                                                   image_dir_name[model_name],
                                                                                   reversion_id,
                                                                                   image_model_name[model_name],
                                                                                   version_number),
                    '%s build_image/linux.deb %s%s/pica-linux-%s-%s-%s.deb' % (copyCmd,
                                                                                dirIp,
                                                                                image_dir_name[model_name],
                                                                                reversion_id,
                                                                                image_model_name[model_name],
                                                                                version_number),
                    '%s build_image/tools.deb %s%s/pica-tools-%s-%s-%s.deb' % (copyCmd,
                                                                                dirIp,
                                                                                image_dir_name[model_name],
                                                                                reversion_id,
                                                                                image_model_name[model_name],
                                                                                version_number), 
                                                                                
                    '%s %s/ovs_bin-%s-%s-%s.tar.gz  %s%s/' % (copyCmd,
                                                                                image_dir_name[model_name],
                                                                                reversion_id,
                                                                                image_model_name[model_name],
                                                                                version_number,
                                                                                dirIp,
                                                                                image_dir_name[model_name]),
                    '%s %s/pica_bin-%s-%s-%s.tar.gz  %s%s/' % (copyCmd,
                                                                                image_dir_name[model_name],
                                                                                reversion_id,
                                                                                image_model_name[model_name],
                                                                                version_number,
                                                                                dirIp,
                                                                                image_dir_name[model_name]),
                    'rm -rf %s/* ' % (image_dir_name[model_name])]                                                                                

                                                                                
        execute_send_expect(child=child, commands=commands)  
    else:
        if model_name in ['as4610_54']:
            onie_platform = 'arm'
        else:
            onie_platform = 'powerpc'      
        copyCmd = 'cp -R' 
        dirIp = ''            
        commands = ['%s build_image/%s.tar.gz %s%s/pica-%s-%s-%s.tar.gz' % (copyCmd, 
                                                                               pica_xorp_map[branch_name],
                                                                               dirIp,
                                                                               image_dir_name[model_name],
                                                                               reversion_id,
                                                                               image_model_name[model_name],
                                                                               version_number),
                    '%s build_image/rootfs.tar.gz %s%s/picos-%s-%s-%s.tar.gz' % (copyCmd,
                                                                                  dirIp,
                                                                                  image_dir_name[model_name],
                                                                                  reversion_id,
                                                                                  image_model_name[model_name],
                                                                                  version_number),
                    '%s build_image/picos_onie_installer.bin %s%s/onie-installer-%s-%s-picos-%s-%s.bin' % (copyCmd,
                                                                                                   dirIp,
                                                                                                   image_dir_name[model_name],
                                                                                                   onie_platform,
                                                                                                   onie_name_map[model_name],
                                                                                                   reversion_id,
                                                                                                   version_number),
                    '%s build_image/ovs.deb %s%s/pica-ovs-%s-%s-%s.deb' % (copyCmd,
                                                                            dirIp,
                                                                            image_dir_name[model_name],
                                                                            reversion_id,
                                                                            image_model_name[model_name],
                                                                            version_number),
                    '%s build_image/xorp.deb %s%s/pica-switching-%s-%s-%s.deb' % (copyCmd,
                                                                                   dirIp,
                                                                                   image_dir_name[model_name],
                                                                                   reversion_id,
                                                                                   image_model_name[model_name],
                                                                                   version_number),
                    '%s build_image/linux.deb %s%s/pica-linux-%s-%s-%s.deb' % (copyCmd,
                                                                                dirIp,
                                                                                image_dir_name[model_name],
                                                                                reversion_id,
                                                                                image_model_name[model_name],
                                                                                version_number),
                    '%s build_image/tools.deb %s%s/pica-tools-%s-%s-%s.deb' % (copyCmd,
                                                                                dirIp,
                                                                                image_dir_name[model_name],
                                                                                reversion_id,
                                                                                image_model_name[model_name],
                                                                                version_number)] 
                     
        execute_send_expect(child=child, commands=commands)

        
###### Execute main 
def execute_main(server_ip=None,branch_name=None, 
                model_name=None, is_license=None, is_sdk=None, 
                brand_name=None, company_name=None, platform_name=None, 
                host_name=None, sbrand_name=None, depend_version=None):

    if model_name in ["as5712_54x"] and server_ip not in ["10.10.50.22"]:
        print 'platform of as5712_54x image can only be built on 10.10.50.22!'
        sys.exit()
    if model_name in ['HP5712'] and server_ip not in ['10.10.50.22']:
        print 'platform of HP5712 image can only be built on 10.10.50.22! '

    if model_name in ["niagara2632xl"] and server_ip not in ["10.10.50.22"]:
        print 'platform of niagara2632xl image can only be built on 10.10.50.22!'
        sys.exit()
        
    if model_name in ["niagara2948_6xl"] and server_ip not in ["10.10.50.22"]:
        print 'platform of niagara2948_6xl image can only be built on 10.10.50.22!'
        sys.exit()      
        
    if model_name in ['dcs7032q28'] and server_ip not in ['10.10.50.22']:
        print 'platform of dcs7032q28 image can only be built on 10.10.50.22!'
        sys.exit()
    
    if is_license == '0':
       is_license = ""
    else:
        is_license = '--with-license'

    if brand_name is None:
        brand_name='Pica8'
    if company_name is None:
        company_name='Pica8, Inc'
    if platform_name is None:
        platform_name='PicOS'
    if host_name is None:
        host_name='XorPlus'  
    if sbrand_name is None:
        sbrand_name='pica8'          

    print '******The value is_license:', is_license
    print '******The value is_sdk:', is_sdk
    print '******The value brand_name:', brand_name   
    print '******The value company_name:', company_name
    print '******The value platform_name:', platform_name  
    print '******The value host_name:', host_name
    print '******The value sbrand_name:', sbrand_name 
    
    print "\n************ SVN ************\n"    
    execute_svn_update(server_ip=server_ip, branch_name=branch_name, model_name=model_name)
    current_version = get_version_number(server_ip=server_ip, branch_name=branch_name, model_name=model_name)
    reversion_id = get_id_number(server_ip=server_ip, branch_name=branch_name, model_name=model_name)

    if depend_version is None:
        depend_version = current_version
        
    if is_sdk == '0':
        print "\n************ PICA Make ************\n"    
        execute_pica_make(server_ip=server_ip, 
                         branch_name=branch_name, 
                         model_name=model_name, 
                         is_license=is_license, 
                         brand_name=brand_name,
                         company_name=company_name,
                         platform_name=platform_name, 
                         host_name=host_name,
                         current_version=current_version,
                         reversion_id=reversion_id)
        print "\n************ OVS Make ************\n"
        execute_ovs_make(server_ip=server_ip, 
                        branch_name=branch_name, 
                        model_name=model_name,  
                        is_license=is_license,   
                        sbrand_name=sbrand_name,
                        current_version=current_version,
                        reversion_id=reversion_id)
        print "\n************ OMS Make ************\n"
        execute_oms_make(server_ip=server_ip, 
                        branch_name=branch_name, 
                        model_name=model_name)
        print "\n************ OS Make ************\n"
        execute_os_make(server_ip=server_ip, 
                       branch_name=branch_name,  
                       model_name=model_name,
                       current_version=current_version, 
                       depend_version=depend_version, 
                       reversion_id=reversion_id)   
    else:  
        print "\n************ SDK Make ************\n"
        execute_sdk_make(server_ip=server_ip, 
                       branch_name=branch_name,  
                       model_name=model_name,
                       current_version=current_version, 
                       depend_version=depend_version, 
                       reversion_id=reversion_id)         
        print "\n************ PICA Make ************\n"    
        execute_pica_make(server_ip=server_ip, 
                         branch_name=branch_name, 
                         model_name=model_name, 
                         is_license=is_license,
                         brand_name=brand_name,
                         company_name=company_name,
                         platform_name=platform_name, 
                         host_name=host_name,
                         current_version=current_version,
                         reversion_id=reversion_id)
        print "\n************ OVS Make ************\n"
        execute_ovs_make(server_ip=server_ip, 
                        branch_name=branch_name, 
                        model_name=model_name,  
                        is_license=is_license,  
                        sbrand_name=sbrand_name,
                        current_version=current_version,
                        reversion_id=reversion_id)
        print "\n************ OMS Make ************\n"
        execute_oms_make(server_ip=server_ip, 
                        branch_name=branch_name, 
                        model_name=model_name)
        print "\n************ OS Make ************\n"
        execute_os_make(server_ip=server_ip, 
                       branch_name=branch_name,  
                       model_name=model_name,
                       current_version=current_version, 
                       depend_version=depend_version, 
                       reversion_id=reversion_id)   
    print "\n************ Image Copy ************\n"
    execute_image_copy(server_ip=server_ip, branch_name=branch_name, model_name=model_name, reversion_id=reversion_id, version_number=current_version)        

print 'You entered: ', len(sys.argv), 'arguments......'
print 'they are: ', str(sys.argv)

if len(sys.argv) < 6:
    print "\n********You are missing some parameters********\n"
    print Usage
    sys.exit(1)
elif len(sys.argv) == 6:
    branch_name,server_ip,model_name,is_license,is_sdk= [w for w in sys.argv[1:]]
    execute_main(server_ip=server_ip, branch_name=branch_name, 
                model_name=model_name, is_license=is_license,is_sdk=is_sdk) 
elif len(sys.argv) == 11:
    branch_name,server_ip,model_name,is_license,is_sdk,brand_name,company_name,platform_name,host_name,sbrand_name= [w for w in sys.argv[1:]]
    execute_main(server_ip=server_ip, branch_name=branch_name, 
                model_name=model_name, is_license=is_license,is_sdk=is_sdk,brand_name=brand_name, company_name=company_name,platform_name=platform_name, host_name=host_name, sbrand_name=sbrand_name)                   
else:
    branch_name,server_ip,model_name,is_license,is_sdk,brand_name,company_name,platform_name,host_name,sbrand_name,depend_version= [w for w in sys.argv[1:]]
    execute_main(server_ip=server_ip, branch_name=branch_name, 
                model_name=model_name, is_license=is_license,is_sdk=is_sdk,brand_name=brand_name,company_name=company_name,platform_name=platform_name,host_name=host_name,sbrand_name=sbrand_name,depend_version=depend_version)
