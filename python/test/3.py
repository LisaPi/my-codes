#!/usr/bin/python

import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.10.51.145',username = 'admin',password='pica8')
cmd="cd"
stdin,stdout,stderr = ssh.exec_command(cmd)
cmd = 'ls -lt'
stdin,stdout,stderr = ssh.exec_command(cmd)
print stdout.readlines()
