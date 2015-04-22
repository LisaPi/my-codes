#!/usr/bin/python 
# -*- coding: utf-8 -*-

'''
Created on 2014-10-08
@author: beyondzhou
@name: cliCommLib.py
'''

import re
import myglobals

# cli check command
def cliCheckCmd(ssh, cmd, match):
    
    '''Example:
        from login import loginCli
        
        ssh = loginCli()
        cmd = 'version'
        match = 'Pica8'
        cliCheckCmd(ssh, cmd, match)
        sssh.close()
    '''

    if re.search("^ovs", cmd, re.IGNORECASE):
        if re.search("ovs-vswitchd|ovsdb-server|ovs-vlan-bug-workaround|ovs-bugtool", cmd, re.IGNORECASE):
            cmd = '/ovs/sbin/%s' % cmd
        else:
            cmd = '/ovs/bin/%s' % cmd
                
    stdin, stdout, stderr = ssh.exec_command(cmd)
    subject = stdout.readlines()
    
    # convert list into string 
    subject = ''.join(subject)   
    
    if stdin:
        print stdin
    if stderr:
        print stderr
        
    if re.search(match, subject, re.IGNORECASE):
        print 'Expect:\n%s' % match
        print 'Actual:\n%s' % subject
        print '%s check Pass!' % cmd
        return subject
    else:
        myglobals.g_iResult = 1
        print 'Expect:\n%s' % match
        print 'Actual:\n%s' % subject
        print '%s check Fail!' % cmd
        return subject
    
# cli run command
def cliRunCmd(ssh, cmds):
    
    '''Example:
        from login import loginCli
        ssh = loginCli()
        cmds = 'ls'
        cliRunCmd(ssh, cmds)
        ssh.close()
    '''
    
    for cmd in cmds.split('\n'):
        if cmd == '':
            continue
        
        if re.search("^ovs", cmd, re.IGNORECASE):
            if re.search("ovs-vswitchd|ovsdb-server|ovs-vlan-bug-workaround|ovs-bugtool", cmd, re.IGNORECASE):
                cmd = '/ovs/sbin/%s' % cmd
            else:
                cmd = '/ovs/bin/%s' % cmd
                
        stdin, stdout, stderr = ssh.exec_command(cmd)  
        subject = stdout.readlines()  
        subject = ''.join(subject)
        if stdin:
            print stdin
        if stderr:
            print stderr
        print 'Running:\n'    
        print 'admin@PicOS-OVS$ %s' % cmd
        print '%s' % subject
        
# cli capture command
def cliCapCmd(ssh, cmd):
    
    '''Example:
        from login import loginCli
        ssh = loginCli()
        cmd = 'ls'
        subject = cliCapCmd(ssh, cmd)
        ssh.close()
    '''
    
    if re.search("^ovs", cmd, re.IGNORECASE):
        if re.search("ovs-vswitchd|ovsdb-server|ovs-vlan-bug-workaround|ovs-bugtool", cmd, re.IGNORECASE):
            cmd = '/ovs/sbin/%s' % cmd
        else:
            cmd = '/ovs/bin/%s' % cmd
                
    stdin, stdout, stderr = ssh.exec_command(cmd)  
    subject = stdout.readlines()  
    subject = ''.join(subject)
    print subject
    if stdin:
        print stdin
    if stderr:
        print stderr
        
    print 'Running:\n'    
    print 'admin@PicOS-OVS$ %s' % cmd
    print '%s' % subject
             
    return subject

# cli bridge number
def cliBridgeNum(ssh):
    
    '''Example:
        from login import loginCli
        ssh = loginCli()
        subject = cliBridgeNum(ssh)
        ssh.close()
    '''
    
    cmd = 'ovs-vsctl show | grep Bridge'
    
    if re.search("^ovs", cmd, re.IGNORECASE):
        if re.search("ovs-vswitchd|ovsdb-server|ovs-vlan-bug-workaround|ovs-bugtool", cmd, re.IGNORECASE):
            cmd = '/ovs/sbin/%s' % cmd
        else:
            cmd = '/ovs/bin/%s' % cmd
                
    stdin, stdout, stderr = ssh.exec_command(cmd)  
    subject = stdout.readlines()  
    subject = ''.join(subject)
    print subject
    if stdin:
        print stdin
    if stderr:
        print stderr
        
    print 'Running:\n'    
    print 'admin@PicOS-OVS$ %s' % cmd
    print '%s' % subject
      
    result = re.findall("(?s)Bridge", subject)
    number = len(result) 
    
    return number

# cli ovs-vsctl/ovs-ofctl cmd information
def cliBridgeCmd(ssh, cmd):
    
    '''Example:
        from login import loginCli
        ssh = loginCli()
        cmd = 'ovs-vsctl show'
        subject = cliBridgeCmd(ssh, cmd)
        ssh.close()
    '''

    if re.search("^ovs", cmd, re.IGNORECASE):
        if re.search("ovs-vswitchd|ovsdb-server|ovs-vlan-bug-workaround|ovs-bugtool", cmd, re.IGNORECASE):
            cmd = '/ovs/sbin/%s' % cmd
        else:
            cmd = '/ovs/bin/%s' % cmd
                
    stdin, stdout, stderr = ssh.exec_command(cmd)  
    if re.search("dump-meter", cmd):
        subject = stderr.readlines()
    else:
        subject = stdout.readlines()  
    subject = ''.join(subject)
    print 'subject:', subject
    if stdin:
        print stdin
    if stderr:
        print stderr
        
    print 'Running:\n'    
    print 'admin@PicOS-OVS$ %s' % cmd
    print '%s' % subject
    
    return subject

# cli bridge reset
def cliBridgeReset(cli):
    
    '''Example:
        from login import loginCli
        ssh = loginCli()
        cliBridgeReset(ssh)
        ssh.close()
    '''
    
    result = cliCapCmd(cli, "ovs-vsctl show | grep Bridge")
    print result
    bridges = re.findall('(?i)Bridge "?(.*[^\n\r"])"?', result)
    print 'bridges:', bridges,
    if len(bridges) != 0:
        for index in range(len(bridges)):
            cliRunCmd(cli, "ovs-vsctl del-br %s" % bridges[index])
    
# get all ports name list through cli
def cliPortsNameList(cli):
 
    '''Example:
        from login import loginCli
        ssh = loginCli()
        portsNameList = cliPortsNameList(ssh)
        ssh.close()
    '''
    
    subject = cliCapCmd(cli, "cat /pica/bin/pica_default.boot | grep igabit-ethernet")
    portsNameList = re.findall('(?s)"(.*?)"', subject)
    
    return portsNameList

# get all ports id list through cli
def cliPortsIdList(cli):
 
    '''Example:
        from login import loginCli
        ssh = loginCli()
        portsNameList = cliPortsIdList(ssh)
        ssh.close()
    '''
    
    hardwareModel = cliHardwareModel(cli)
    if re.search("P-5401|as6701_32x", hardwareModel, re.DOTALL):
        eid = 32
    elif re.search("P-3780|P-5101", hardwareModel, re.DOTALL):
        eid = 48
    else:
        eid = 52
        
    subject = cliCapCmd(cli, "cat /pica/bin/pica_default.boot | grep igabit-ethernet")
    portsIdList = re.findall("(?s)1/1/([0-9]+)", subject)
    
    return portsIdList[:eid]

# get hardware model through cli
def cliHardwareModel(cli):
 
    '''Example:
        from login import loginCli
        ssh = loginCli()
        hardwareModel = cliHardwareModel(ssh)
        ssh.close()
    '''
    
    subject = cliCapCmd(cli, "version")
    match = re.search(r"Hardware Model\s+:\s+([-a-zA-Z0-9]+)", subject, re.DOTALL)
    if match:
        hardwareModel = match.group(1)
    else:
        hardwareModel = ""
        
    return hardwareModel