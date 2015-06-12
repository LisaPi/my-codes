#! /usr/bin/env python

"""
Created on 2015-06-12
@author: lisapi
@name: api.py
"""


#import some lib
import pexpect
import sys
import re
import os
import pxssh
import time


#login server
def ssh_login(ip=None,user=None,password=None):
    loginprompt = '[$#>]'
    s=pxssh.pxssh()
    s.login (ip, user, password,original_prompt=loginprompt, login_timeout=1000000)

    return s

    
#Expect and send 
def sendExpect(child=None, command=None):

    prompt = '[$#>]'
    child.sendline ('%s' % command)
    child.expect('(.*)%s' % prompt) 
    print "%s%s" % (child.after,child.before)

    return child.before, child.after
                  
