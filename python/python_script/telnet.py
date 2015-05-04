#!/usr/bin/env python

import getpass
import telnetlib

HOST = "10.10.51.149"
user = raw_input("Enter your remote account: ")
password = getpass.getpass()
tn = telnetlib.Telnet(HOST)

tn.read_until(b"XorPlus login:")
print '11'
tn.write(user.encode('ascii') +b"\n")
print '22'
if password:
    print '33'
    tn.read_until(b"Password:")
    tn.write(password.encode('ascii') + b"\n")

print '44'
tn.read_until(b"admin@XorPlus$")
print '55'
tn.write(b"ls\n")
print '66'
print tn.read_all()
print '77'
tn.write(b"cli\n")
tn.write(b"exit\n")

print(tn.read_all().decode('ascii'))

