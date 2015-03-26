#!/usr/bin/python


import  paramiko

def ssh2(ip,username,passwd,cmd):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,22,username,passwd,timeout=5)
        for m in cmd:
            stdin, stdout, stderr = ssh.exec_command(m)
            out = stdout.readlines()
            err = stderr.readlines()
            for o in out:
                print o
            for o in err:
                print o
        ssh.close()
    except :
         print '%s\t login failed\n'%(ip)
    



if __name__=='__main__':
    
    port = ['ge-1/1/3']
    cmds = ['version','ls -lt','/pica/bin/pica_sh -c "configure;set interface gigabit-ethernet ge-1/1/3 disable true;commit"']
    username = "admin" 
    passwd = "pica8"
    ssh2("10.10.51.145", username, passwd, cmds)
    



