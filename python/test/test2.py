#!/usr/bin/python

import pxssh
import getpass
import sys
import time
try:
    s=pxssh.pxssh()
    hostname="10.10.50.42"
    username="root"
    password=getpass.getpass('password:')
    loginprompt = '[$#>]'
    s.login(hostname, username, password, original_prompt=loginprompt)
    s.sendline('pwd')
    s.expect('%s' % loginprompt)
    print "%s%s" % (s.after,s.before)
    s.sendline('ls -l')
    s.expect('%s' % loginprompt)
    print "%s%s" % (s.after,s.before)
    s.logout
except pxssh.ExceptionPxssh, e:
       print "pxssh failed on login."
       print str(e)
