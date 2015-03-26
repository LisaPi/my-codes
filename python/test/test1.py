#!/usr/bin/python

import pxssh
import getpass

try:
    s=pxssh.pxssh()
    hostname=raw_input('address:')
    username=raw_input('Username:')
    password=getpass.getpass('password:')
    loginprompt = '[$#>]'
    s.login(hostname, username, password, original_prompt=loginprompt)
    s.sendline('pwd')
    s.prompt()
    s.sendline('ls -l')
    s.prompt()
    print s.before
    s.logout
except pxssh.ExceptionPxssh, e:
       print "pxssh failed on login."
       print str(e)
