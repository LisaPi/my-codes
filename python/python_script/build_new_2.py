#! /usr/bin/env python

"""
The script is used to build images,
supporting branches, 1.1  2.6 2.6B verizon
supporting models, 3290 3295 3297 3922 3924 3930 3780 5401 es4654bf as6701_32x as5712_54x niagara2632xl arctica4804i

Usage:

./build.py branch_name server_ip model_name svn_type is_license depend_version

branch_name,      the name of branch (eg, 1.1)
server_ip,        the server of code (eg. 10.10.50.16)
model_name,       the name of model (eg. 3290)
svn_type:         the type of svn (0: del and svn, 1: only svn, 2: do not svn)
is_license:       the image is licensed (0: no-license, 1: license)
depend_version:   the depend version of image (set it as current version if it is none)

Example:

./build.py 1.1 10.10.50.16 3290 1 1 

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

branch_id_name = ['1.1', '2.6', 'verizon', '2.6B']
model_type_name = ['3290', '3295', '3297', '3920', '3922', '3924', '3930', '3780', '5401', '5101', 'es4654bf', 'as6701_32x', 'as5712_54x', 'niagara2632xl', 'arctica4804i']


# Build specific pica xorplus map 
pica_xorp_map = {'1.1': 'xorplus',
                 '2.6': 'pica',
                 '2.6B':'xorplus',
                 'verizon': 'xorplus'}

# Build sdk mapping table             
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
               'as5712_54x': 'sdk-xgs-robo-6.3.9',
               'arctica4804i': 'sdk-xgs-robo-6.3.2'}
               

sdk_loc_name = {}
for model in model_type_name:
    sdk_loc_name[model] = sdk_dict[model] 

# Build specific sdk id map 
sdk_id_map = {'1.1': '',
              '2.6': '',
              '2.6B':'',
              'verizon': ''}    
            
# Build kernel mapping table      
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
                   'as5712_54x': 'linux-3.4.82-x86_64',
                   'arctica4804i': 'linux-3.2.35-onie'}

kernel_loc_name = {}
for model in model_type_name:
    kernel_loc_name[model] = kernel_dict[model]   
        
# Build powerpcspe mapping table
ppc_dict = {'1.1': 'rootfs-debian-basic',
               '2.6': 'rootfs-debian-basic',
               'verizon': 'rootfs-debian-basic',
               '2.6B': 'rootfs-debian-basic'}

ppc_loc_name = {}
for branch in branch_id_name:
    ppc_loc_name[branch] = ppc_dict[branch]

# Build box name under os
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
               'as5712_54x': 'as5712_54x',
               'arctica4804i': 'arctica4804i'}

os_box_name = {}
for model in box_name_map:
    os_box_name[model] = box_name_map[model]

#Build box name  
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
               'as5712_54x': 'as5712_54x',
               'arctica4804i': 'arctica4804i'}
    
    
# Build os directory 
os_name_map = {'1.1': 'os-dev',
               '2.6': 'os-dev',
               'verizon': 'os-dev',
               '2.6B': 'os-dev'}
               
os_dir_name = {}
for branch in branch_id_name:
    os_dir_name[branch] = os_name_map[branch]

# Build relative directory 
rel_name_map = {'1.1': '.',
               '2.6': '.',
               'verizon': '.',
               '2.6B': '.'}
               
rel_dir_name = {}
for branch in branch_id_name:
    rel_dir_name[branch] = rel_name_map[branch]

# Build cross compile
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
                    'as5712_54x': '',
                    'arctica4804i': 'powerpc-linux-gnuspe'}

cross_compile_name = {}
for model in cross_compile_map:
    cross_compile_name[model] = cross_compile_map[model]

# User info
user_name = 'build'
user_password = 'build'
prompt = '[$#>]'

# Build pica config name
pica_config_name = {}
for branch in branch_id_name:
    pica_config_name.setdefault(branch, {})
    for model in model_type_name:
        if model in ['as5712_54x', 'niagara2632xl']:
            sDirs = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model).group(), branch)
            hTmp = rel_dir_name[branch]
            oDir = os_dir_name[branch]
            hType = cross_compile_name[model]
            sNoDug = '--disable-debug'
            sOpt = '--enable-optimize'
            sBox = model
            sLib =  sdk_loc_name[model]
            sBcm = "bcm_"+re.search("([.0-9]+)", sLib).group()    
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
                                        ' % (sDirs, hTmp, oDir, model, pica_xorp_map[branch], hType, sNoDug, sOpt, box_name_map[model] , sDirs,sBcm, box_map[model], sDirs, hTmp, sLib)  
        elif model in ['arctica4804i']:
            sDirs = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model).group(), branch)
            hTmp = rel_dir_name[branch]
            oDir = os_dir_name[branch]
            hType = cross_compile_name[model]
            sNoDug = '--disable-debug'
            sOpt = '--enable-optimize'
            sBox = model
            sLib =  sdk_loc_name[model]
            pica_config_name[branch][model] = './configure --prefix=%s/%s/%s/%s/rootfs-debian/%s \
                                          --host=%s \
                                          --enable-static=no %s %s \
                                          --with-pronto%s \
                                          --with-lcmgr=yes \
                                        --with-rootfs_debian=yes \
                                        ovs_cv_use_linker_sections=yes \
                                        --with-chip_sdk_lib_path=%s/pica/exlib/bcm_6.3.2.%s \
                                        --with-chip_sdk_deprecated_version=no \
                                        --with-chip_sdk_root_path=%s/%s/sdk/%s \
                                        ' % (sDirs, hTmp, oDir, box_name_map[model], pica_xorp_map[branch], hType, sNoDug, sOpt, '3296' ,sDirs, model, sDirs, hTmp, sLib)                                         
        else:
            sDirs = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model).group(), branch)
            hTmp = rel_dir_name[branch]
            oDir = os_dir_name[branch]
            hType = cross_compile_name[model]
            sNoDug = '--disable-debug'
            sOpt = '--enable-optimize'
            sBox = model
            sLib =  sdk_loc_name[model]
            sBcm = "bcm_"+re.search("([.0-9]+)", sLib).group()  
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
                                        ' % (sDirs, hTmp, oDir, box_name_map[model], pica_xorp_map[branch], hType, sNoDug, sOpt, box_name_map[model] ,sDirs, sBcm,box_map[model], sDirs, hTmp, sLib)               

# Build ovs config name
host_type_map = {'3290': 'powerpc-linux',
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
                 'as5712_54x': '',
                 'arctica4804i': 'powerpc-linux-gnuspe'}
                 
# Build ovs model name
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
                    'as5712_54x': 'as5712_54x',
                    'arctica4804i': 'arctica4804i'}
                    

ovs_config_name = {}
for branch in branch_id_name:
    ovs_config_name.setdefault(branch, {})
    for model in model_type_name:
        if model in ['as5712_54x', 'es4654bf', 'as6701_32x', 'niagara2632xl']:
            hType = host_type_map[model]
            pBox = ovs_model_map[model]
            ovs_config_name[branch][model] = './configure --host=%s --with-%s -with-switchdir=/ovs \
                                               ' % (hType, pBox)
        elif model in ['arctica4804i']:
            hType = host_type_map[model]
            pBox = '%s%s' % ('3296','new')
            ovs_config_name[branch][model] = './configure --host=%s --with-pronto%s -with-switchdir=/ovs \
                                               ' % (hType, pBox)
        else:
            hType = host_type_map[model]
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
               'niagara2632xl': 'accton_niagara2632xl',
               'as5712_54x': 'accton_as5712_54x',
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
               'as5712_54x': 'as5712_54x',
               'arctica4804i': 'arctica4804i'}

# Build image directory ame
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
               'as5712_54x': '/tftpboot/%s/daily/as5712_54x' % user_name,
               'arctica4804i': '/tftpboot/%s/daily/arctica4804i' % user_name}

# Send email
def excute_send_email(err_subject=None, err_buffer=None, current_version=None, branch_name=None):
    
    who = 'build@pica8.local'
    whos = "lpi@pica8.local"

    origBody = '''\
From: %(who)s
To: %(whos)s
Subject: %(subject)s

%(err_buffer)s

Version:%(current_version)s
Branch:%(branch_name)s
''' % {'who': who, 'whos':whos,'subject': err_subject, 
       'err_buffer': err_buffer, 'current_version': current_version,
       'branch_name': branch_name}

    sendSvr = SMTP(SMTPSVR)
    errs = sendSvr.sendmail(who, [whos], origBody)
    sendSvr.quit()
    assert len(errs) == 0, errs
    sleep(10)
                       
# Usage
def exit_with_usage():
    print globals()['__doc__']
    os._exit(1)

# Server login
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

# Excute send and expect
def excute_send_expect(child=None, commands=None, exp_prompt=None, err_subject=None, current_version=None, branch_name=None):
    
    if exp_prompt is None:
        exp_prompt = prompt
        
    for command in commands:
        if command == 'make -j8':
            child.sendline ('%s' % command)
            i = child.expect(['([\s\S]{100}Error )', '%s@.*%s' % (user_name, exp_prompt)], timeout=None)
            if i == 0:
                err_buffer = child.match.group(1)
                excute_send_email(err_subject=err_subject, err_buffer=err_buffer, 
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
   
# Svn update
def excute_svn_update(server_ip=None, svn_type=None, branch_name=None, model_name=None):

    # Get spawn id
    child = server_ssh_login(server_ip=server_ip)
    
    # Switch to desc directory
    dest_dir = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model_name).group(), branch_name)
    excute_send_expect(child=child, commands=['cd %s' % dest_dir])
    
    # Sdk update
    excute_send_expect(child=child, commands=['rm -rf %s/sdk/%s' % (rel_name_map[branch_name],
                                                                    sdk_loc_name[model_name])])
    excute_send_expect(child=child, commands=['svn update %s %s/sdk/%s' % (sdk_id_map[branch_name],
                                                                           rel_name_map[branch_name], 
                                                                           sdk_loc_name[model_name])])
    # Branch update
    if svn_type == 0:
        commands = [
                    'sudo rm -rf *', 
                    'sudo rm -rf %s/%s/%s' % (rel_name_map[branch_name], os_dir_name[branch_name], os_box_name[model_name]), 
                    'sudo rm -rf %s/%s/%s' % (rel_name_map[branch_name], os_dir_name[branch_name], ppc_loc_name[branch_name]),
                    'sudo rm -rf %s/%s/%s' % (rel_name_map[branch_name], os_dir_name[branch_name], kernel_loc_name[model_name]),
                    'svn up %s/%s/%s' % (rel_name_map[branch_name], os_dir_name[branch_name], os_box_name[model_name]), 
                    'svn up %s/%s/%s' % (rel_name_map[branch_name], os_dir_name[branch_name], ppc_loc_name[branch_name]),
                    'svn up %s/%s/%s' % (rel_name_map[branch_name], os_dir_name[branch_name], kernel_loc_name[model_name]),
                    'svn up',
                    'ls | grep -v os-dev | grep -v sdk | xargs chown -R %s' % user_name,
                    'ls | grep -v os-dev | grep -v sdk | xargs chgrp -R %s' % user_name]

        excute_send_expect(child=child, commands=commands)   
                    
    elif svn_type == 1:
        commands = [ 
                    'svn up %s/%s/%s' % (rel_name_map[branch_name], os_dir_name[branch_name], os_box_name[model_name]), 
                    'svn up %s/%s/%s' % (rel_name_map[branch_name], os_dir_name[branch_name], ppc_loc_name[branch_name]),
                    'svn up %s/%s/%s' % (rel_name_map[branch_name], os_dir_name[branch_name], kernel_loc_name[model_name]),
                    'svn up',
                    'ls | grep -v os-dev | grep -v sdk | xargs chown -R %s' % user_name,
                    'ls | grep -v os-dev | grep -v sdk | xargs chgrp -R %s' % user_name]
                    
        excute_send_expect(child=child, commands=commands)   
            
    else:       
        commands = [ 
                'ls | grep -v os-dev | grep -v sdk | xargs chown -R %s' % user_name,
                'ls | grep -v os-dev | grep -v sdk | xargs chgrp -R %s' % user_name,
                'chown -R %s %s/%s/%s' % (user_name, rel_name_map[branch_name], os_dir_name[branch_name], box_name_map[model_name]),
                'chgrp -R %s %s/%s/%s' % (user_name, rel_name_map[branch_name], os_dir_name[branch_name], box_name_map[model_name])]
    
        excute_send_expect(child=child, commands=commands)

# Get the rId number
def get_id_number(server_ip=None, branch_name=None, model_name=None):                    

    # Get spawn id
    child = server_ssh_login(server_ip=server_ip)

    # Switch to desc directory
    dest_dir = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model_name).group(), branch_name)
    excute_send_expect(child=child, commands=['cd %s' % dest_dir])

    child.sendline('grep support@pica8.org configure.ac')
    child.expect('pica,\s+\[([0-9a-zA-Z.]+)\]')
    id_num = child.match.group(1)

    if branch_name in ['1.1']:
        id_num = '1.1'

    return id_num

# Get the version number
def get_version_number(server_ip=None, branch_name=None, model_name=None):                    

    # Get spawn id
    child = server_ssh_login(server_ip=server_ip)
    
    # Switch to desc directory
    dest_dir = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model_name).group(), branch_name)
    excute_send_expect(child=child, commands=['cd %s' % dest_dir])
    
    child.sendline('svn info')
    child.expect('Last Changed Rev:\s+([0-9]+)')
    version = child.match.group(1)
    
    return version
        
# Xorp make and install
def excute_xorp_make(server_ip=None, branch_name=None, 
                     model_name=None, is_license=None, 
                     current_version=None, reversion_id=None):

    # Get spawn id
    child = server_ssh_login(server_ip=server_ip)
    
    # Switch to desc directory
    dest_dir = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model_name).group(), branch_name)
    excute_send_expect(child=child, commands=['cd %s' % dest_dir])
    
    # export CROSS_COMPILE, bootstrap, configure, make -j8, make install
    sDirs = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model_name).group(), branch_name)
    hTmp = rel_dir_name[branch_name]
    oDir = os_dir_name[branch_name]
    commands = [
                'export CROSS_COMPILE=%s-' % cross_compile_name[model_name],
                './bootstrap',
                '%s %s' % (pica_config_name[branch_name][model_name], is_license),
                'make -j8',
                'make install',
                'cd %s/%s/%s/%s/rootfs-debian/%s' % (sDirs,hTmp,oDir,box_name_map[model_name],pica_xorp_map[branch_name]),
                'tar -czvf /tftpboot/%s/daily/%s/pica_bin-%s-%s-%s.tar.gz bin/*' % (user_name, model_name, reversion_id, model_name, current_version),
                'cd %s' % dest_dir,
                'make install-strip'
                ]
    excute_send_expect(child=child, commands=commands, err_subject='%s Pica make error!' % model_name, current_version=current_version, branch_name=branch_name)
        
# Ovs make 
def excute_ovs_make(server_ip=None, branch_name=None, 
                    model_name=None,is_license=None,
                    current_version=None, reversion_id=None):

    # Get spawn id
    child = server_ssh_login(server_ip=server_ip)
    
    # Switch to desc directory
    ovs_version = 'openvswitch-2.3.0'
    dest_dir = '/home/%s/%s/release/pica8/branches/%s/ovs/%s' % (user_name, re.search("([0-9]{4})", model_name).group(), branch_name,ovs_version)
    excute_send_expect(child=child, commands=['cd %s' % dest_dir])
   
    # export CROSS_COMPILE, configure, make -j8, make install
    sDirs = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model_name).group(), branch_name)
    hTmp = rel_dir_name[branch_name]
    oDir = os_dir_name[branch_name]
    if model_name in ['es4654bf']:
        ovs_model_name = 'as4600_54t'
    elif model_name in ['3924']:
        ovs_model_name = 'as5600_52x'
    else:
        ovs_model_name = model_name

    commands = [
                'export CROSS_COMPILE=%s-' % cross_compile_name[model_name],
                'autoreconf --install --force',
                '%s %s --prefix=%s/%s/%s/%s/rootfs-debian/ovs' % (ovs_config_name[branch_name][model_name], is_license, sDirs, hTmp, oDir, box_name_map[model_name]),
                'make -j8',
                'make install',
                'tar -czvf /tftpboot/%s/daily/%s/ovs_bin-%s-%s-%s.tar.gz bin/*' % (user_name, ovs_model_name, reversion_id,ovs_model_name, current_version),
                'make install-strip',
                'make install-xlib-strip'
                ]
    excute_send_expect(child=child, commands=commands, err_subject='%s Ovs %s make error!' % (model_name, ovs_version), current_version=current_version, branch_name=branch_name)
    
# Oms make
def excute_oms_make(server_ip=None, branch_name=None, model_name=None):

    # Get spawn id
    child = server_ssh_login(server_ip=server_ip)
    
    # Switch to desc directory
    dest_dir = '/home/%s/%s/release/pica8/branches/%s/ovs/oms' % (user_name, re.search("([0-9]{4})", model_name).group(), branch_name)
    excute_send_expect(child=child, commands=['cd %s' % dest_dir])
   
    # python build.py
    sDirs = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model_name).group(), branch_name)
    hTmp = rel_dir_name[branch_name]
    oDir = os_dir_name[branch_name]  
    excute_send_expect(child=child, commands=['python build.py %s %s/%s/%s v2.0' % (model_name, sDirs, hTmp, oDir)])
    
# Os make
def excute_os_make(server_ip=None, branch_name=None, 
                   model_name=None, current_version=None, 
                   depend_version=None, reversion_id=None):

    # Get spawn id
    child = server_ssh_login(server_ip=server_ip)
    
    sDirs = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model_name).group(), branch_name)
    hTmp = rel_dir_name[branch_name]
    oDir = os_dir_name[branch_name]
                
    # Switch to desc directory
    dest_dir = '%s/%s/%s/%s' % (sDirs, hTmp, oDir, box_name_map[model_name])
    excute_send_expect(child=child, commands=['cd %s' % dest_dir])
   
    # export CROSS_COMPILE_PATH, CROSS_COMPILE, PATH
    commands = [
                  'export CROSS_COMPILE=%s' % cross_compile_name[model_name],
                  'export CROSS_COMPILE_PATH=/tools/eldk4.2/usr/',
                  'export PATH=$CROSS_COMPILE_PATH/bin:$PATH',
                   ]
    excute_send_expect(child=child, commands=commands)
    
    if model_name not in ['as5712_54x', 'niagara2632xl']:
        commands = [
                'export ARCH=powerpc',
                ]
        excute_send_expect(child=child, commands=commands) 
        
    # make fast
    sDirs = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model_name).group(), branch_name)
    hTmp = rel_dir_name[branch_name]
    sLib =  sdk_loc_name[model_name]
    oDir = os_dir_name[branch_name]       
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
       
    if model_name in ['as5712_54x', 'niagara2632xl']:
        lBox = string.upper(box_name_map[model_name])
        commands = [
                'sudo make fast PICA8=1 %s=1 SDK=%s/%s/sdk/%s BRANCH=%s%s' % (lBox, sDirs, hTmp,
                                                                              sLib,branch_name,sRevison)
                ]
    else:
        lBox = string.upper(box_name_map[model_name])
        commands = [
                'sudo make fast %s=1 SDK=%s/%s/sdk/%s BRANCH=%s%s' % (lBox, sDirs, hTmp, sLib,branch_name,sRevison)  
                    ]      
    excute_send_expect(child=child, commands=commands)   
    
# Build_image_copy
def excute_image_copy(server_ip=None, branch_name=None, model_name=None, reversion_id=None, version_number=None):
    
    # Get spawn id
    child = server_ssh_login(server_ip=server_ip)
    
    sDirs = '/home/%s/%s/release/pica8/branches/%s' % (user_name, re.search("([0-9]{4})", model_name).group(), branch_name)
    hTmp = rel_dir_name[branch_name]
    oDir = os_dir_name[branch_name]
                
    # Switch to desc directory
    dest_dir = '%s/%s/%s/%s' % (sDirs, hTmp, oDir, box_name_map[model_name])
    excute_send_expect(child=child, commands=['cd %s' % dest_dir])
    
    # Do the copy
    if model_name in ['as5712_54x', 'niagara2632xl']:
        ppcOrX86 = 'x86'
        copyCmd = 'scp'
        dirIp = '%s@10.10.50.16:' % user_name
    else:
        ppcOrX86 = 'powerpc'      
        copyCmd = 'cp -R' 
        dirIp = ''
            
    commands = ['%s build_image/%s.tar.gz %s/%s/pica-%s-%s-%s.tar.gz' % (copyCmd, 
                                                                               pica_xorp_map[branch_name],
                                                                               dirIp,
                                                                               image_dir_name[model_name],
                                                                               reversion_id,
                                                                               image_model_name[model_name],
                                                                               version_number),
                    '%s build_image/rootfs.tar.gz %s/%s/picos-%s-%s-%s.tar.gz' % (copyCmd,
                                                                                  dirIp,
                                                                                  image_dir_name[model_name],
                                                                                  reversion_id,
                                                                                  image_model_name[model_name],
                                                                                  version_number),
                    '%s build_image/picos_onie_installer.bin %s/%s/onie-installer-%s-%s-picos-%s-%s.bin' % (copyCmd,
                                                                                                   dirIp,
                                                                                                   image_dir_name[model_name],
                                                                                                   ppcOrX86,
                                                                                                   onie_name_map[model_name],
                                                                                                   reversion_id,
                                                                                                   version_number),
                    '%s build_image/ovs.deb %s/%s/pica-ovs-%s-%s-%s.deb' % (copyCmd,
                                                                            dirIp,
                                                                            image_dir_name[model_name],
                                                                            reversion_id,
                                                                            image_model_name[model_name],
                                                                            version_number),
                    '%s build_image/xorp.deb %s/%s/pica-switching-%s-%s-%s.deb' % (copyCmd,
                                                                                   dirIp,
                                                                                   image_dir_name[model_name],
                                                                                   reversion_id,
                                                                                   image_model_name[model_name],
                                                                                   version_number),
                    '%s build_image/linux.deb %s/%s/pica-linux-%s-%s-%s.deb' % (copyCmd,
                                                                                dirIp,
                                                                                image_dir_name[model_name],
                                                                                reversion_id,
                                                                                image_model_name[model_name],
                                                                                version_number),
                    '%s build_image/tools.deb %s/%s/pica-tools-%s-%s-%s.deb' % (copyCmd,
                                                                                dirIp,
                                                                                image_dir_name[model_name],
                                                                                reversion_id,
                                                                                image_model_name[model_name],
                                                                                version_number)] 
                     
    excute_send_expect(child=child, commands=commands)
        
# Excute main 
def excute_main(server_ip=None, svn_type=None, branch_name=None, 
                model_name=None, is_license=None, depend_version=None):

    if model_name in ["as5712_54x"] and server_ip not in ["10.10.50.22"]:
        print 'as5712_54x image can only be built at 10.10.50.22!'
        sys.exit()

    if model_name in ["niagara2632xl"] and server_ip not in ["10.10.50.22"]:
        print 'niagara2632xl image can only be built at 10.10.50.22!'
        sys.exit()

    if is_license == '0':
        is_license = ""
    else:
        is_license = '--with-license'

    svn_type = int(svn_type)
    print 'is_license:', is_license
    print 'svn_type:', svn_type

    print "\n**********SVN Clean/Up**********\n"
    excute_svn_update(server_ip=server_ip, svn_type=svn_type, branch_name=branch_name, model_name=model_name)
    current_version = get_version_number(server_ip=server_ip, branch_name=branch_name, model_name=model_name)
    reversion_id = get_id_number(server_ip=server_ip, branch_name=branch_name, model_name=model_name)

    if depend_version is None:
        depend_version = current_version

    print "\n********PICA Make**********\n"   
    excute_xorp_make(server_ip=server_ip, 
                     branch_name=branch_name, 
                     model_name=model_name, 
                     is_license=is_license,                         
                     current_version=current_version,
                     reversion_id=reversion_id)
                     
    print "\n********OVS Make**********\n"
    excute_ovs_make(server_ip=server_ip, 
                    branch_name=branch_name, 
                    model_name=model_name, 
                    is_license=is_license,                         
                    current_version=current_version,
                    reversion_id=reversion_id)
                    
    print "\n***********OMS Make********\n"
    excute_oms_make(server_ip=server_ip, 
                    branch_name=branch_name, 
                    model_name=model_name)
                    
    print "\n**********OS Make**********\n"
    excute_os_make(server_ip=server_ip, 
                   branch_name=branch_name,  
                   model_name=model_name,
                   current_version=current_version, 
                   depend_version=depend_version, 
                   reversion_id=reversion_id)
    
    print "\n********** Image Copy**********\n"
    excute_image_copy(server_ip=server_ip, branch_name=branch_name, model_name=model_name, reversion_id=reversion_id, version_number=current_version)

# Entrance to main
print 'You entered: ', len(sys.argv), 'arguments...'
print 'they are: ', str(sys.argv)

if len(sys.argv) < 6:
    print "\n*********You are missing some parameters********\n"
    exit_with_usage()
elif len(sys.argv) == 6:
    branch_name,server_ip,model_name,svn_type,is_license= [w for w in sys.argv[1:]]
    excute_main(server_ip=server_ip, svn_type=svn_type, branch_name=branch_name, 
                model_name=model_name, is_license=is_license)
    
else:
    branch_name,server_ip,model_name,svn_type,is_license,depend_version= [w for w in sys.argv[1:]]
    excute_main(server_ip=server_ip, svn_type=svn_type, branch_name=branch_name, 
                model_name=model_name, is_license=is_license,depend_version=depend_version)
