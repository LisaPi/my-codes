#!/usr/bin/python


import time
import re
import pexpect 
import pxssh
import paramiko

def ssh_login(ip,user,password):
    loginprompt = '[$#>]'
    s = pxssh.pxssh()
    s.login (ip, user, password,original_prompt=loginprompt, login_timeout=1000000)
    return s 


def sendExpect(child, command, prompt):

    prompt = '[$#>]'
    child.sendline ('%s' % command) 
    child.expect('(.*)%s' % prompt) 
    print "%s%s" % (child.after,child.before)
   
    return child.before,child.after


def checkCmd (child, command, expect_value):
    
    prompt = '[$#>]'
    child.sendline ('%s' % command)
    child.expect('(.*)%s' % prompt)
    match = child.match.group()
    flag = re.search('%s' % expect_value, match)
    return flag 
    

def pica8_config(ip, user, password, directory, ports):
    prompt = '[$#>]'

    #check the ovs process and cd dir
    child = ssh_login(ip,user,password)
    sendExpect(child, 'ps', prompt)
    sendExpect(child, 'cd %s' % directory, prompt)
    sendExpect(child, 'ls -lt', prompt)
    sendExpect(child, 'ovs-vsctl show', prompt)
    return child


def LoginCli(ip,username,passwd):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip,22,username,passwd,timeout=5)
    return ssh

def Xorp_config(ip,user,password):
    
    prompt = '[$#>]'

    #login sw and send linux commands
    child = ssh_login(ip,user,password)
    sendExpect(child, 'pwd', prompt)
    return child

