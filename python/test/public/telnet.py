#!/usr/bin/env python

import pexpect
import os
import sys


ip = '10.10.51.145'
user = 'admin'
password = 'pica8'
prompt = '[$#>]'
cmd = 'telnet ' + ip

child = pexpect.spawn(cmd)
index = child.expect(['XorPlus login:',pexpect.EOF,pexpect.TIMEOUT],timeout=15)
if index == 0:
    child.sendline(user)
    print child.before,child.after
    index = child.expect('assword:',timeout=15)
    child.sendline(password)
    print child.before,child.after
    child.expect(prompt,timeout=10)
    child.sendline('version')
    print child.after,child.before
else:
    print ('expect "login",but get EOF or TIMEOUT')

#child.close()

