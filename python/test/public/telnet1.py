#!/usr/bin/env python

import pexpect
import os
import sys


ip = '10.10.51.145'
user = 'admin'
password = 'pica8'
prompt = '[$#>]'
cmd=['pwd','version']

def telnet_login(ip=None):
    child = pexpect.spawn('telnet %s' % (ip))
    while True:
        i = child.expect(['\$', 'XorPlus login:'])
        if i == 0:
            child.sendline('')
            break
        elif i == 1:
            child.sendline('%s' % user)
            child.expect('assword:')
            print child.before,child.after
            child.sendline('%s' % password)
    child.expect(prompt)
    child.sendline('version')
    print child.before,child.after
    child.expect(prompt)
    print child.before,child.after

    return child

if __name__ == '__main__':
    telnet_login(ip='10.10.51.145')
