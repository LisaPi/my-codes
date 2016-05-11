#! /usr/bin/env python

import pexpect
conn = False
import sys

try:
    child = pexpect.spawn("telnet 10.10.50.90", timeout= 100)
    child.logfile = sys.stdout
    conn = True
except:
    print ' some exception occured'

if conn:
    child.expect(":", timeout = 10)
    child.sendline('apc')
    child.expect(":", timeout = 10)
    child.sendline('apc')
    child.expect(">")
