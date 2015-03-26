#!/usr/bin/python


import pxssh
import pexpect
import os 


def pica8_login(ip,username,password,command,port=22):
    try:
        #prompt = '[$#>]'
        s = pxssh.pxssh()
        s.login(ip,username,password)
        for cmd in command:
            s.sendline(cmd)
            s.prompt()
            print s.before
        s.logout()
    except pxssh.ExceptionPxssh, e:
        print "Login failed"
        print str(e)



def info():
    ip = '10.10.51.145'
    username = 'admin'
    password = 'pica8'
    command = ['pwd','version','license -s']
    return ip,username,password,command



def user():
    ip = '10.10.51.145'
    username = 'admin'
    password = 'pica8'
    return ip,username,password


def userinfo():
    ip = '10.10.51.161'
    username = 'admin'
    password = 'pica8'
    directory = '/ovs'
    br = 'br0'
    ports = ['ge-1/1/1','ge-1/1/2','ge-1/1/3','ge-1/1/4']
    cmds = ['ovs-vsctl del-br br0','ovs-vsctl add-br br0 -- set bridge br0 datapath_type=pica8','ovs-vsctl list bridge']
    return ip,username,password,directory,ports,cmds

def xorpinfo():
    ip = '10.10.51.161'
    username = 'admin'
    password = '123456789'
    port = ['ge-1/1/1','ge-1/1/2','ge-1/1/3','ge-1/1/4']
    cmd = ['ls -lt','version']
    return ip,username,password,port,cmd
