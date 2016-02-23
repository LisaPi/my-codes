#!/usr/bin/env python

import sys
import pexpect
from ftplib import FTP
import os
import os.path
import time

host_name = "ftp.pica8.org"
User_name = "engineer@pica8.org"
password = "bj_development?8"
loginprompt = 'ftp>'

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
print child.before,child.after
child.expect(loginprompt,timeout=10)
#child.sendline('mkdir release-3.0')
#print child.before,child.after
#child.expect(loginprompt,timeout=10)
child.sendline('rmdir  release-3.1')
print child.before,child.after
child.expect(loginprompt,timeout=10)
child.sendline('exit')
print child.before,child.after
