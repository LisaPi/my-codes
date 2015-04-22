#! /usr/bin/env python

"""

Usage:
./consoleErr.py switch_ip
switch_ip,        the ip of switch

Example:
./consoleErr.py 10.10.51.134
"""

import os
import pexpect
import sys
import re

prompt = '[$#>]'
user_name = 'admin'
user_password = 'pica8'

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
        child.sendline ('%s' % command)
        i = child.expect(['(failed opcode was)', '%s@.*%s' % (user_name, exp_prompt)], timeout=None)
        if i == 0:
            err_buffer = child.match.group(1)
            sys.exit()

# Entrance
def main(ip_address=None):

    # Login
    child = server_ssh_login(server_ip=ip_address)
    child.sendline('cli')
    child.expect(prompt)
    child.sendline('configure')
    child.expect(prompt)

    # Config
    commands = ['set interface aggregate-ethernet ae1', 
                'commit', 
                'delete interface aggregate-ethernet ae1', 
                'commit', 
                'set vlans vlan-id 2000',
                'commit',
                'set vlans vlan-id 2000 l3-interface vlan-2000',
                'commit',
                 'delete vlans vlan-id 2000 l3-interface',
                 'commit',
                 'delete vlans vlan-id 2000',
                 'commit']
    while True:
        excute_send_expect(child=child, commands=commands)        

if __name__ == '__main__':
    
    if len(sys.argv) < 2:
        exit_with_usage()
    else:
        main(ip_address=sys.argv[1])
