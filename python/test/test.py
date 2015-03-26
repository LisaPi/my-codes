#!/usr/bin/python
# Filename: auto_ssh.py

import pexpect
import pxssh

def auto_ssh_cmd(ip,username,password,command,port=22):
    try:
        remote = pxssh.pxssh()
        remote.login(ip,username,password)
        remote.sendline(command)
        remote.prompt()
        print remote.before
        remote.logout()
    except pxssh.ExceptionPxssh, e:
           print "pxssh failed on login."
           print str(e)



auto_ssh_cmd('10.10.50.42','root','pica8','ls -lt',port=22)
