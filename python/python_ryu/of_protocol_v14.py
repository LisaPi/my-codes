from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_4
from ryu.ofproto import ofproto_v1_4_parser
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib import mac
from ryu.lib.mac import haddr_to_str

# Generate any number mac address being in incr order
def inceaseMac(self, num=None, mac=None):
    # Change the mac address format into list with its value type is string
    macs = mac.split(':')

    # Change the string list into int list
    #macs = map(int, macs)
    macs = [int(x, 16) for x in macs]

    # Change the value of list into hex format
    macs = ''.join('%02x'%i for i in macs)
    tmp = '0x'
    macs = tmp + macs
    macs = int(macs,16)

    # Generate mac address
    sMacs = []
    for i in range(macs, macs + num):
        j = (i >> 40) & 0xFF
        k = format(j, "02x")
        sMac = k

        j = (i >> 32) & 0x00FF
        k = format(j, "02x")
        sMac = sMac + ':' + k

        j = (i >> 24) & 0x0000FF
        k = format(j, "02x")
        sMac = sMac + ':' + k

        j = (i >> 16) & 0x000000FF
        k = format(j, "02x")
        sMac = sMac + ':' + k

        j = (i >> 8) & 0x00000000FF
        k = format(j, "02x")
        sMac = sMac + ':' + k

        j = i & 0x0000000000FF
        k = format(j, "02x")
        sMac = sMac + ':' + k

        sMacs.append(sMac)

    # Return the mac list
    return sMacs

# Generate mac address at random
def randomMAC(self):
    import random
    mac = [ 0x00, 0x16, 0x3e, random.randint(0x00, 0x7f), random.randint(0x00, 0xff), random.randint(0x00, 0xff) ]
    return ':'.join(map(lambda x: "%02x" % x, mac))

# Change ipv4 to int format
def ipv4_to_int(self, string):
    ip = string.split('.')
    assert len(ip) == 4
    i = 0
    for b in ip:
        b = int(b)
        i = (i << 8) | b
    return i
