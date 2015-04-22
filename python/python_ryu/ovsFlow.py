#!/usr/bin/env python

import pexpect
import os
import sys
import re

user_name = 'admin'
user_password = 'pica8'
prompt = '[$#>]'

# Generate any number mac address in incr order
def gene_incr_mac(num=None, mac=None):
    # Change the mac address format into list with its value type is string
    macs = mac.split(':')

    # Change the string list into int list
    #macs = map(int, macs)
    macs = [int(x, 16) for x in macs]

    # Change the value of list into hex format
    macs = ''.join('%02x'%i for i in macs)
    tmp = '0x'
    macs = tmp + macs
    macs = int(macs,16)

    # Generate mac address
    sMacs = []
    for i in range(macs, macs + num):
        j = (i >> 40) & 0xFF
        k = format(j, "02x")
        sMac = k

        j = (i >> 32) & 0x00FF
        k = format(j, "02x")
        sMac = sMac + ':' + k

        j = (i >> 24) & 0x0000FF
        k = format(j, "02x")
        sMac = sMac + ':' + k

        j = (i >> 16) & 0x000000FF
        k = format(j, "02x")
        sMac = sMac + ':' + k

        j = (i >> 8) & 0x00000000FF
        k = format(j, "02x")
        sMac = sMac + ':' + k

        j = i & 0x0000000000FF
        k = format(j, "02x")
        sMac = sMac + ':' + k

        sMacs.append(sMac)
    return sMacs

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

macs = gene_incr_mac(num=5000, mac='22:00:00:00:00:00')
child = server_ssh_login(server_ip='10.10.51.150')
for mac in macs:
    excute_send_expect(child=child, commands=['ovs-ofctl add-flow br0 in_port=1,dl_dst=%s,actions=all' % mac])
