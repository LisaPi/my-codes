#! /usr/bin/env python

Usage = """
Created on 2016-5-21
@author: lisapi
@name: git clone repo
The script is used to clone repo from remote

Usage:

./copy_image.py  sDr,sRevision,branch_name,model

sDr,      the name of release dir name
sRevision,        the revison name
branch_name,      the version name on daiy dir image
model:      the platform name

Example:

./copy_image.py 2.7 22244  1.1 3290
"""

#import some lib
import pexpect
import re 
import pxssh
import time
import sys

user_name= "build"
user_password = 'build'
prompt = '[$#>]'
server_ip = '10.10.50.16'
git_password="pica8build"
model_name="3930"
branch="master"
 
try:
    s=pxssh.pxssh() 
    loginprompt = '[$#>]'
    s.login(server_ip, user_name, user_password, original_prompt=prompt,login_timeout=9000)
    s.sendline('pwd')
    s.expect('%s' % prompt)
    print "%s%s" % (s.after,s.before)
    s.sendline('cd /home/build/%s/release/pica8/branches' %model_name)
    s.expect('%s' % prompt)
    print "%s%s" % (s.after,s.before)
    s.sendline('git clone http://code.pica8.local/repo/pica8.git')
    print "%s%s" % (s.after,s.before)    
    s.expect('Username for')    
    print "%s%s" % (s.after,s.before)    
    s.sendline('%s' % user_name)
    s.expect('Password for')
    print "%s%s" % (s.after,s.before)    
    s.sendline('%s' % git_password)
    s.expect('%s' % prompt)    
    print "%s%s" % (s.after,s.before)
    s.sendline('mv pica8 %s' % branch)  
    s.expect('%s' % prompt) 
    print "%s%s" % (s.after,s.before)   
    s.logout
except pxssh.ExceptionPxssh, e:
       print "pxssh failed on login."
       print str(e)

