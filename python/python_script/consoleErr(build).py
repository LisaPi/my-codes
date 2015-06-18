#! /usr/bin/env python

import os
import pexpect

prompt = '[$#>]'
user_name = 'root'
user_password = 'pica8'

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
            i = child.expect(['(failed opcode was)', '%s@.*%s' % (user_name, exp_prompt)], timeout=None)
            if i == 0:
                err_buffer = child.match.group(1)
                excute_send_email(err_subject=err_subject, err_buffer=err_buffer, current_version=current_version, branch_name=branch_name)
                sys.exit()
        else:   
            if re.search('scp', command):
                child.sendline ('%s' % command)
                while True:
                    i = child.expect(['\$', 'yes/no', 'assword:'])
                    if i == 0:
                        child.sendline('')
                        break
                    elif i == 1:
                        child.sendlist('yes')
                    else:
                        child.sendline('%s' % user_password)
            else:
                child.sendline ('%s' % command)
                child.expect(pattern='%s@.*%s' % (user_name, exp_prompt), timeout=None)

# Entrance
def main(ip_address=None):

    # Login
    child = server_ssh_login(server_ip=ip_address)
    child.sendline('cli')
    child.expect(prompt)
    child.sendline('configure')
    child.expect(prompt)

    # Config
    commands = [['set interface aggregate-ethernet ae1'], ['commit'], ['delete interface aggregate-ethernet ae1'], ['commit']]
    while True:
        excute_send_expect(child=child, commands=commands)        

if __name__ == '__main__':
    main(ip_address='10.10.51.134')
