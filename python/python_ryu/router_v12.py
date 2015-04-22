# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import struct
import array
import socket
import time

from types import *
from ryu.controller import handler
from ryu.base import app_manager
from ryu.controller import mac_to_port
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_2
from ryu.ofproto import ether
from ryu.lib.mac import haddr_to_str
from ryu.lib.packet import packet
from ryu.lib.packet import *
from ryu.lib.packet import arp
from ryu.lib.packet import ethernet
from ryu.lib.packet import icmp
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp
from ryu.lib.packet import udp
from ryu.lib.packet import vlan
from ryu.lib import mac

UINT16_MAX = 0xffff
UINT32_MAX = 0xffffffff
UINT64_MAX = 0xffffffffffffffff

LOG = logging.getLogger('ryu.app.simple_switch')

# TODO: we should split the handler into two parts, protocol
# independent and dependant parts.

# TODO: can we use dpkt python library?

# TODO: we need to move the followings to something like db


class SimpleRouter(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_2.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleRouter, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

    #self.debug control
    debug_arp = 1
    debug_mac = 1
    debug_route = 1
    debug_other = 2
    debug_pktin = 1

    #Configure the system MAC address
    sys_mac = '08:9E:01:61:65:E9'
    
    #Init the ARP table
    arp_table = {}
    #local_arp = {'10.10.50.1': sys_mac,'10.10.53.1': sys_mac,
                     #'10.10.70.1': sys_mac,'10.10.71.1': sys_mac}
    local_arp = {'10.10.50.1': sys_mac,'10.10.53.1': sys_mac,
                     '10.10.51.1': sys_mac,'10.10.70.1': sys_mac,
                     '10.10.71.1': sys_mac}
    static_arp = {'10.10.70.2': '00:1E:68:0F:4C:86'}
    arp_table.update(local_arp)
    arp_table.update(static_arp)
    if debug_arp == 1:
        LOG.info("::::::Init the ARP table as following:")
        LOG.info("%s", arp_table)

    #Init the vlan-interface and member table
    #vlan_table = {'vlan2': [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16], 
                    #'vlan3': [19,20,21,22],
                    #'vlan5': [25,26,27,28],
                    #'vlan10': [18],
                    #'vlan9': [17]}
    vlan_table = {'vlan1': [41,42,43,44,45,46,47,48],
                    'vlan2': [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16], 
                    'vlan3': [19,20,21,22],
                    'vlan4': [23,24],
                    'vlan5': [25,26,27,28],
                    'vlan6': [29,30,31,32,33,34],
                    'vlan7': [35,36],
                    'vlan8': [37,38,39,40],
                    'vlan10': [18],
                    'vlan9': [17]}  
    LOG.info(":::Init the vlan_table as follows:")
    LOG.info("%s", vlan_table)

    #Init the route table, in here, we support static router
    route_table = [['0.0.0.0/0.0.0.0','vlan9','static','10.10.70.2'],
                   ['10.10.50.0/255.255.255.0','vlan2','connected', None],
                   ['10.10.53.0/255.255.255.0','vlan5','connected', None],
                   ['10.10.51.0/255.255.255.0','vlan3','connected', None],
                   ['10.10.70.0/255.255.255.0','vlan9','connected', None],
                   ['10.10.71.0/255.255.255.0','vlan10','connected', None]]
                   #['0.0.0.0/0.0.0.0','vlan9','static','10.10.71.2']]
    LOG.info(":::Init the route_table as follows:")
    LOG.info("%s", route_table)  
                   
    #static mac for next hop, later, will remove this
    #mac_next_hop = {'10.10.71.2': '22:00:00:00:00:00','10.10.70.2': '22:00:00:00:00:01'}
    #mac_next_hop = {'10.10.70.2': '22:00:00:00:00:01'}

    #Init the FDB table, in here, we support mac learning or static mac
    mac_table = {'00:1E:68:0F:4C:86': 17}
                   
    #Find the route according the dest-ip
    def lookupRoute(self, dstIp, routeTable):
        dst_ip_split = dstIp.split('.')
        dst_ip_split[3] = '0/255.255.255.0'
        dst_ip_net = '.'.join(dst_ip_split)
        route_lookup = []
        default_route_entry = []
        for route_entry in routeTable:
            if route_entry[0] == '0.0.0.0/0.0.0.0' :
                default_route_entry=route_entry
        
        if self.debug_other == 2:
            LOG.info("::The IP_net of %s is %s", dstIp, dst_ip_net)
        
        for route_entry in routeTable:
            if dst_ip_net == route_entry[0]:
                route_lookup.append(route_entry)
        if route_lookup == [] :
            route_lookup.append(default_route_entry)
            
        if self.debug_route == 1:
            LOG.info("::The lookup route table result is %s", route_lookup)
        return route_lookup[0]
        
    #Check is it a ECMP route or not
    def checkEcmpRoute(route_entry_lookup):
        if len(route_entry_lookup) > 1:
            return true
        else:
            return false

    #Get the output port of the route entry
    def getRouteOutports(route_entry):
        out_vlan = route_entry[1]
        out_ports = vlan_table['out_vlan']
        return out_ports                                                #############need accurate outport

    #Get the next-hope of the route entry
    def getRouteNextHop(route_entry):
        next_hop = route_entry[3]
        return next_hop

    #Get the MAC address from ARP table
    def getMacForIP(ip_add):
        for arp_entry in self.arp_table:
            if ip_add == mac_entry[0]:                            ##############mac_entry? 
                mac_add = mac_entry[1]
        return mac_add

    #Update the output port of the route entry accoridng FDB table
    def updateRouteOutport(out_ports,mac):
        for mac_entry in mac:
            mac == mac_entry[0]
            for port in out_ports:
                if port == mac_entry[1]:
                    return port
                else:
                    return out_ports

    #send ARP request 
    def sendArp(self, datapath, arp_opcode, vlan_id, src_mac, dst_mac,
                 src_ip, dst_ip, arp_target_mac, in_port, output):                         
        # Generate ARP packet
        if vlan_id != 0:
            ether_proto = ether.ETH_TYPE_8021Q
            pcp = 0
            cfi = 0
            vlan_ether = ether.ETH_TYPE_ARP
            v = vlan.vlan(pcp, cfi, vlan_id, vlan_ether)
        else:
            ether_proto = ether.ETH_TYPE_ARP
        hwtype = 1
        arp_proto = ether.ETH_TYPE_IP
        hlen = 6
        plen = 4

        pkt = packet.Packet()
        e = ethernet.ethernet(dst_mac, src_mac, ether_proto)
        a = arp.arp(hwtype, arp_proto, hlen, plen, arp_opcode,
                    src_mac, src_ip, arp_target_mac, dst_ip)
        pkt.add_protocol(e)     
        if vlan_id != 0:
            pkt.add_protocol(v)
        pkt.add_protocol(a)
        pkt.serialize()

        # Send packet out
        self.send_packet_out(datapath, in_port, output, pkt.data, data_str=str(pkt)) 

    def send_packet_out(self, datapath, in_port, output, data, data_str=None):
        actions = [datapath.ofproto_parser.OFPActionOutput(output, 0)] 
        datapath.send_packet_out(buffer_id=0xffffffff, in_port=in_port,
                                actions=actions, data=data)

    def updateFlowWithArp(self,datapath,arp_src_ip,arp_src_mac,in_port):
        #add a ip flow and should be higher pri than MAC FDB
        match = self.match_v12(datapath, dl_type=0x0800, ipv4_dst=arp_src_ip,      #######dl_type=0x0800   not to add an arpflow, but an ip flow
                                 dl_dst=self.sys_mac)
        actions = self.action_v12(datapath, out_port=in_port, dl_src=self.sys_mac, dl_dst=arp_src_mac)
        self.flow_v12(datapath, priority=2000, table_id=0, match=match, flags=1, 
                           command=0, buffer_id=0xffffffff, actions=actions)
        LOG.info(":::Add host route according ARP: %s", arp_src_ip)                    
        
    def arpProcess(self, datapath, in_port, pkt, msg):
        arp = self.find_protocol(pkt, 'arp')
        arp_hwtype = arp.hwtype
        arp_proto = arp.proto
        arp_hlen = arp.hlen
        arp_plen = arp.plen
        arp_opcode = arp.opcode
        #arp_src_mac = haddr_to_str(arp.src_mac)
        arp_src_mac = arp.src_mac      
        #arp_src_ip = socket.inet_ntoa(struct.pack('I',socket.htonl(arp.src_ip)))      ###eg.10.10.50.100
        arp_src_ip = arp.src_ip
        #arp_dst_mac = haddr_to_str(arp.dst_mac)            ########arp.dst_mac 00:00:00:00:00:00
        arp_dst_mac = arp.dst_mac
        #arp_dst_ip = socket.inet_ntoa(struct.pack('I',socket.htonl(arp.dst_ip)))       ###eg.10.10.50.10
        arp_dst_ip = arp.dst_ip
        #anyway, learn the arp and update the flow according src
        self.arp_table[arp_src_ip] = arp_src_mac
        self.updateFlowWithArp(datapath,arp_src_ip,arp_src_mac,in_port)
        #it is free arp
        if arp_src_ip == arp_dst_ip:
            #####flood arp 
            output = datapath.ofproto.OFPP_FLOOD
            actions = [datapath.ofproto_parser.OFPActionOutput(output,0)]
            out = datapath.ofproto_parser.OFPPacketOut(
                datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port,
                actions=actions)
            datapath.send_msg(out)
            return
        #it is arp request to local gateway
        if arp_dst_ip in self.local_arp: 
            #make sure it is a request and reply the arp for local system mac
            if arp_opcode == 1:
                self.sendArp(datapath=datapath, arp_opcode=2, 
                     src_mac=self.sys_mac, vlan_id=0,
                     dst_mac=arp.src_mac, src_ip=arp.dst_ip, dst_ip=arp.src_ip,   
                    #arp_target_mac=mac.haddr_to_bin(self.sys_mac), in_port=0, 
                     arp_target_mac=arp.src_mac, in_port=0,         
                     output=in_port)
            else:
                #normal arp request/reply, just update and flood
                output = self.ofctl.dp.ofproto.OFPP_FLOOD
                datapath.send_packet_out(msg.buffer_id, msg.in_port)
        else:
            output = datapath.ofproto.OFPP_FLOOD                                                                            
            actions = [datapath.ofproto_parser.OFPActionOutput(output,0)]
            print msg
            out = datapath.ofproto_parser.OFPPacketOut(
                datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port,
                actions=actions)
            datapath.send_msg(out)
        return

    def ipProcess(self, datapath, in_port, pkt,msg):
        ipv4 = self.find_protocol(pkt, 'ipv4')
        ip_version = ipv4.version
        ip_header_length = ipv4.header_length
        ip_tos = ipv4.tos
        ip_total_length = ipv4.total_length
        ip_identification = ipv4.identification
        ip_flags = ipv4.flags
        ip_offset = ipv4.offset
        ip_ttl = ipv4.ttl
        ip_proto = ipv4.proto
        ip_csum = ipv4.csum
        #ip_src = socket.inet_ntoa(struct.pack('I',socket.htonl(ipv4.src)))
        ip_src = ipv4.src
        #ip_dst = socket.inet_ntoa(struct.pack('I',socket.htonl(ipv4.dst)))
        ip_dst = ipv4.dst
        ip_option = ipv4.option
        #if dest_ip is not belonged to local networkseg, it should not happened, because it 
        #should be matched by hardware flow, it should be local host
        route_result = self.lookupRoute(dstIp=ip_dst, routeTable=self.route_table)
        if route_result[2] == 'connected':            
            #send arp request to update the arp table, then, discard the packet
            self.sendArp(datapath=datapath, arp_opcode=1, vlan_id=0, src_mac=self.sys_mac,         
                 dst_mac='ff:ff:ff:ff:ff:ff',
                 src_ip=ipv4.src, dst_ip=ipv4.dst,
                 arp_target_mac='00:00:00:00:00:00', in_port=in_port,                    
                 output=datapath.ofproto.OFPP_FLOOD)
            return
        #flood broadcast in vlan
        elif ip_dst == '255.255.255.255' or ip_dst == '0.0.0.0':
            for m in self.vlan_table:
                if in_port in self.vlan_table[m]:
                     out_ports = self.vlan_table[m]
                     break
            output = out_ports
            actions = []
            if type(output) is ListType:
                for outPort in output:
                    actions.append(datapath.ofproto_parser.OFPActionOutput(outPort, 0))
            elif type(output) is IntType:
                actions.append(datapath.ofproto_parser.OFPActionOutput(output, 0))
            out = datapath.ofproto_parser.OFPPacketOut(
                datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port,
                actions=actions)
            datapath.send_msg(out)                   
        else:
            LOG.info(":::Warning, received un-expected packet which should forward gw.")
            return

    #install the defalt flow according the route table
    def installDefaultFlow(self,datapath):
        #get the route table and install the default gw
        #TO BE DONE, switch should trigger a ARP request to install the route dynamic
        for route_entry in self.route_table:
            if route_entry[2] == 'static':
                ip_net = route_entry[0]
                ipstr = ip_net.split('/')
                ip_dst = ipstr[0]
                ip_mask = ipstr[1]
                vlan_if = route_entry[1]
                nextHop = route_entry[3]
                #nextHopMac = self.mac_next_hop[nextHop]
                nextHopMac = self.arp_table[nextHop]
                outports = self.vlan_table[vlan_if]
                if nextHopMac in self.mac_table:
                    outport = self.mac_table[nextHopMac]
                else:
                    outport = outports
                #priority value, if ip/mask= x.x.x.x/x
                ipmasks = ip_mask.split('.')
                index = 0
                for x in ipmasks:
                    x=int(x)
                    if x==0:
                        ipmasks=index*8
                    else:
                        index+=1
                priority=1000+ipmasks
                #install the flows
                match = self.match_v12(datapath, dl_type=0x0800, ipv4_dst=ip_dst, ipv4_dst_mask=ip_mask, dl_dst=self.sys_mac)
                actions = self.action_v12(datapath,dl_dst=nextHopMac, dl_src=self.sys_mac, 
                                            out_port=outport)
                
                self.flow_v12(datapath, priority=priority, table_id=0, match=match, flags=1, 
                           command=0, buffer_id=0xffffffff, actions=actions)
                LOG.info(":::Add static route: %s", ip_net)
            elif route_entry[2] == 'connected':
                ip_net = route_entry[0]
                ipstr = ip_net.split('/')
                ip_dst = ipstr[0]
                ip_mask = ipstr[1]
                vlan_if = route_entry[1]
                outports = datapath.ofproto.OFPP_CONTROLLER
                #priority value, if ip/mask= x.x.x.x/x
                ipmasks = ip_mask.split('.')
                index = 0
                for x in ipmasks:
                    x=int(x)
                    if x==0:
                        ipmasks=index*8
                    else:
                        index+=1
                priority=1000+ipmasks
                #install the flows
                match = self.match_v12(datapath, dl_type=0x0800, ipv4_dst=ip_dst, ipv4_dst_mask=ip_mask)
                actions = self.action_v12(datapath, out_port=outports)
                #miss_send_len = UINT16_MAX
                #actions = [datapath.ofproto_parser.OFPActionOutput(
                           #datapath.ofproto.OFPP_ALL, miss_send_len)]
                self.flow_v12(datapath, priority=priority, table_id=0, match=match, flags=1, 
                           command=0, buffer_id=0xffffffff, actions=actions)
                LOG.info(":::Add connected route: %s", ip_net)               
        return       

    # Generate any number mac address being in incr order
    def inceaseMac(self, num=None, mac=None):
        # Change the mac address format into list with its value type is string
        macs = mac.split(':')

        # Change the string list into int list
        #macs = map(int, macs)
        macs = [int(x, 16) for x in macs]                                 #########int(x,16), change Hex to Dec.

        # Change the value of list into hex format
        macs = ''.join('%02x'%i for i in macs)                           ######? why not macs=''join(macs),  and del macs = [int(x, 16) for x in macs]
        tmp = '0x'
        macs = tmp + macs
        macs = int(macs,16)                                                    ##########?Dec  macs=18838586676582 for add num

        # Generate mac address
        sMacs = []
        for i in range(macs, macs + num):
            j = (i >> 40) & 0xFF
            k = format(j, "02x")                                                    #########? 02x   format()    Dec->Hex
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

    def randomMAC(self):
        import random
        mac = [ 0x00, 0x16, 0x3e, random.randint(0x00, 0x7f), random.randint(0x00, 0xff), random.randint(0x00, 0xff) ]
        return ':'.join(map(lambda x: "%02x" % x, mac)) 


    def match_v12(self, datapath, in_port=None, dl_dst=None, dl_src=None, dl_type=None, 
                 vlan_vid=None, vlan_pcp=None, ip_dscp=None, ip_ecn=None, ip_proto=None, ipv4_src=None, 
                 ipv4_src_mask=None, ipv4_dst=None, ipv4_dst_mask=None, tcp_src=None, tcp_dst=None, 
                 udp_src=None, udp_dst=None):
                 
        match = datapath.ofproto_parser.OFPMatch()
        if in_port is not None:
            match.set_in_port(in_port)
            
        if dl_dst is not None:
            dl_dst = mac.haddr_to_bin(dl_dst)
            match.set_dl_dst(dl_dst)
            
        if dl_src is not None:
            dl_src = mac.haddr_to_bin(dl_src)
            match.set_dl_src(dl_src)
            
        if dl_type is not None:
            match.set_dl_type(dl_type)
            
        if vlan_vid is not None:
            match.set_vlan_vid(vlan_vid)
            
        if vlan_pcp is not None:
            match.set_vlan_pcp(vlan_pcp)
            
        if ip_dscp is not None:
            match.set_ip_dscp(ip_dscp)
            
        if ip_ecn is not None:
            match.set_ip_ecn(ip_ecn)
            
        if ip_proto is not None:
            match.set_ip_proto(ip_proto)
            
        if ipv4_src is not None:
            ipv4_src = self.ipv4_to_int(ipv4_src)
            match.set_ipv4_src(ipv4_src)

        if ipv4_src_mask is not None:
            ipv4_src_mask = self.ipv4_to_int(ipv4_src_mask)
            match.set_ipv4_src_masked(ipv4_src, self.mask_ntob(ipv4_src_mask))
            
        if ipv4_dst is not None:
            ipv4_dst = self.ipv4_to_int(ipv4_dst)
            match.set_ipv4_dst(ipv4_dst)

        if ipv4_dst_mask is not None:
            ipv4_dst_mask = self.ipv4_to_int(ipv4_dst_mask)
            #match.set_ipv4_dst_masked(ipv4_dst, self.mask_ntob(ipv4_dst_mask))
            match.set_ipv4_dst_masked(ipv4_dst, ipv4_dst_mask)

        if tcp_src is not None:
            match.set_tcp_src(tcp_src)
            
        if tcp_dst is not None:
            match.set_tcp_dst(tcp_dst)
            
        if udp_src is not None:
            match.set_udp_src(udp_src)
            
        if udp_dst is not None:
            match.set_udp_dst(udp_dst)

        return match

    def action_v12(self, datapath, actions=None, dl_dst=None, dl_src=None, dl_type=None, 
                          vlan_vid=None, vlan_pcp=None, ip_dscp=None, ip_ecn=None, 
                          ip_proto=None, ipv4_src=None, ipv4_dst=None, tcp_src=None, 
                          tcp_dst=None, udp_src=None, udp_dst=None, out_port=None):

        if actions is not None:
            actions = actions
        else:
            actions = []
                  
        if dl_dst is not None:
            field = datapath.ofproto.OXM_OF_ETH_DST
            out_dl_dst = datapath.ofproto_parser.OFPMatchField.make(field, mac.haddr_to_bin(dl_dst))
            actions = [datapath.ofproto_parser.OFPActionSetField(out_dl_dst), ]
            
        if dl_src is not None:
            field = datapath.ofproto.OXM_OF_ETH_SRC
            out_dl_src = datapath.ofproto_parser.OFPMatchField.make(field, mac.haddr_to_bin(dl_src))
            actions.append(datapath.ofproto_parser.OFPActionSetField(out_dl_src), )
            
        if dl_type is not None:
            field = datapath.ofproto.OXM_OF_ETH_TYPE
            out_dl_type = datapath.ofproto_parser.OFPMatchField.make(field, dl_type)
            actions.append(datapath.ofproto_parser.OFPActionSetField(out_dl_src), )
            
        if vlan_vid is not None:
            field = datapath.ofproto.OXM_OF_VLAN_VID
            out_vlan_vid = datapath.ofproto_parser.OFPMatchField.make(field, vlan_vid)
            actions.append(datapath.ofproto_parser.OFPActionSetField(out_vlan_vid), )

        if vlan_pcp is not None:
            field = datapath.ofproto.OXM_OF_VLAN_PCP
            out_vlan_pcp = datapath.ofproto_parser.OFPMatchField.make(field, vlan_pcp)
            actions.append(datapath.ofproto_parser.OFPActionSetField(out_vlan_pcp), )
            
        if ip_dscp is not None:
            field = datapath.ofproto.OXM_OF_IP_DSCP
            out_ip_dscp = datapath.ofproto_parser.OFPMatchField.make(field, ip_dscp)
            actions.append(datapath.ofproto_parser.OFPActionSetField(out_ip_dscp), )
            
        if ip_ecn is not None:
            field = datapath.ofproto.OXM_OF_IP_ECN
            out_ip_ecn = datapath.ofproto_parser.OFPMatchField.make(field, ip_ecn)
            actions.append(datapath.ofproto_parser.OFPActionSetField(out_ip_ecn), )
            
        if ip_proto is not None:
            field = datapath.ofproto.OXM_OF_IP_PROTO
            out_ip_proto = datapath.ofproto_parser.OFPMatchField.make(field, ip_proto)
            actions.append(datapath.ofproto_parser.OFPActionSetField(out_ip_proto), )
            
        if ipv4_src is not None:
            field = datapath.ofproto.OXM_OF_IPV4_SRC
            out_ipv4_src = datapath.ofproto_parser.OFPMatchField.make(field, self.ipv4_to_int(ipv4_src))
            actions.append(datapath.ofproto_parser.OFPActionSetField(out_ipv4_src), )
            
        if ipv4_dst is not None:
            field = datapath.ofproto.OXM_OF_IPV4_DST
            out_ipv4_dst = datapath.ofproto_parser.OFPMatchField.make(field, self.ipv4_to_int(ipv4_dst))
            actions.append(datapath.ofproto_parser.OFPActionSetField(out_ipv4_dst), )
            
        if tcp_src is not None:
            field = datapath.ofproto.OXM_OF_TCP_SRC
            out_tcp_src = datapath.ofproto_parser.OFPMatchField.make(field, tcp_src)
            actions.append(datapath.ofproto_parser.OFPActionSetField(out_tcp_src), )
            
        if tcp_dst is not None:
            field = datapath.ofproto.OXM_OF_TCP_DST
            out_tcp_dst = datapath.ofproto_parser.OFPMatchField.make(field, tcp_dst)
            actions.append(datapath.ofproto_parser.OFPActionSetField(out_tcp_dst), )
            
        if udp_src is not None:
            field = datapath.ofproto.OXM_OF_UDP_SRC
            out_udp_src = datapath.ofproto_parser.OFPMatchField.make(field, udp_src)
            actions.append(datapath.ofproto_parser.OFPActionSetField(out_udp_src), )
            
        if udp_dst is not None:
            field = datapath.ofproto.OXM_OF_UDP_DST
            out_udp_dst = datapath.ofproto_parser.OFPMatchField.make(field, udp_DST)
            actions.append(datapath.ofproto_parser.OFPActionSetField(out_udp_dst), )

        if out_port is not None:
            if type(out_port) is IntType:
                actions.append(datapath.ofproto_parser.OFPActionOutput(out_port, 0))
            elif type(out_port) is LongType:
                actions.append(datapath.ofproto_parser.OFPActionOutput(out_port, UINT16_MAX))
            elif type(out_port) is ListType:
                for outPort in out_port:
                    actions.append(datapath.ofproto_parser.OFPActionOutput(outPort, 0))
            else:
                print("errorType==============")
        else:
            actions.append(datapath.ofproto_parser.OFPActionOutput(ofproto.OFPP_ALL, 0))
       
        return actions

    def bucket_v12(self, datapath, actions = [], len_=0, weight=0, watch_port=0, watch_group=0):
        buckets = [datapath.ofproto_parser.OFPBucket(len_=len_, weight=weight, watch_port=watch_port,watch_group=watch_group, actions=actions)]
        return buckets

    def group_v12(self, datapath, group_id=0, type_=0, command=0, buckets=None):
        
        group = datapath.ofproto_parser.OFPGroupMod(datapath=datapath,command=command,type_=type_,group_id=group_id,buckets=buckets)
        datapath.send_msg(group)

    def ipv4_to_int(self, string):
        ip = string.split('.')
        assert len(ip) == 4                         ##########how can i know the function of assert
        i = 0
        for b in ip:
            b = int(b)
            i = (i << 8) | b
        return i

    def mask_ntob(self, mask, err_msg=None):                      ##########just support /mask, eg. /24
        try:
            return (UINT32_MAX << (32 - mask)) & UINT32_MAX
        except ValueError:
            msg = 'illegal netmask'
            if err_msg is not None:
                msg = '%s %s' % (err_msg, msg)
            raise ValueError(msg)


    def flow_v12(self, datapath, cookie=0, cookie_mask=0, table_id=0, command=None, idle_timeout=0, hard_timeout=0, \
                 priority=0, buffer_id=0, match=None, actions=None, inst_type=None, out_port=None, out_group=None, flags=0, inst=None):
        if command is None:
            command = datapath.ofproto.OFPFC_ADD

        if inst is None:
            if inst_type is None:
                inst_type = datapath.ofproto.OFPIT_APPLY_ACTIONS
                inst = []
            if actions is not None:
                inst = [datapath.ofproto_parser.OFPInstructionActions(inst_type, actions)]
        if match is None:
            match = datapath.ofproto_parser.OFPMatch()
        if out_port is None:
            out_port = datapath.ofproto.OFPP_ANY
        if out_group is None:
            out_group = datapath.ofproto.OFPG_ANY

        flow = datapath.ofproto_parser.OFPFlowMod(datapath, cookie, cookie_mask, table_id, command, idle_timeout, hard_timeout, priority, buffer_id, \
                                                  out_port, out_group, flags, match, inst)
        datapath.send_msg(flow)
    
    def add_match_v12_dic(self, datapath, in_port=None, dl_dst=None,  \
                  dl_src=None, dl_type=None, vlan_vid=None,   \
                  vlan_pcp=None, ip_dscp=None, ip_ecn=None,   \
                  ip_proto=None, ipv4_src=None, ipv4_dst=None,\
                  tcp_src=None, tcp_dst=None, udp_src=None, udp_dst=None):
        match = datapath.ofproto_parser.OFPMatch()
    
        dCmdFunc = {'in_port':match.set_in_port,   \
                             'dl_dst':match.set_dl_dst,     \
                            'dl_type':match.set_dl_type,   \
                             'vlan_vid':match.set_vlan_vid, \
                            'vlan_pcp':match.set_vlan_pcp, \
                            'ip_dscp':match.set_ip_dscp,   \
                            'ip_ecn':match.set_ip_ecn,     \
                            'ip_proto':match.set_ip_proto, \
                            'ipv4_src':match.set_ipv4_src, \
                            'ipv4_dst':match.set_ipv4_dst, \
                            'tcp_src':match.set_tcp_src,   \
                            'tcp_dst':match.set_tcp_dst,   \
                            'udp_src':match.set_udp_src,   \
                            'udp_dst':match.set_udp_dst}
            
        dCmdKey = {'in_port':in_port,   \
                           'dl_dst':dl_dst,     \
                           'dl_type':dl_type,   \
                           'vlan_vid':vlan_vid, \
                           'vlan_pcp':vlan_pcp, \
                           'ip_dscp':ip_dscp,   \
                           'ip_ecn':ip_ecn,     \
                           'ip_proto':ip_proto, \
                           'ipv4_src':ipv4_src, \
                           'ipv4_dst':ipv4_dst, \
                           'tcp_src':tcp_src,   \
                           'tcp_dst':tcp_dst,   \
                           'udp_src':udp_src,   \
                           'udp_dst':udp_dst}
        
        for key,value in dCmdKey.items():
            print "key:%s value:%s\n" % (key, value)
            if value is not None:
                func = dCmdFunc[key]
                func(value)   

        return match
        
    def find_protocol(self, pkt, name):
        #print(pkt)
        for p in pkt.protocols:
            if hasattr(p, 'protocol_name'):
                if p.protocol_name == name:
                    return p

    def dir_print(self, msg):
        print "%s\n" % dir(msg)

    def packetProcess(self, datapath, in_port, pkt, msg):
        # Mac information
        mac_addr = self.find_protocol(pkt,'ethernet')  
        if mac_addr:
            #mac_src = haddr_to_str(mac_addr.src)
            #mac_dst = haddr_to_str(mac_addr.dst)
            mac_src = mac_addr.src
            mac_dst = mac_addr.dst
            mac_ethertype = mac_addr.ethertype
            if self.debug_pktin == 1:
                LOG.info("mac_src:%s mac_dst:%s mac_ethertype:%s\n",mac_src,mac_dst,mac_ethertype)
            
        # Vlan information
        vlan = self.find_protocol(pkt, 'vlan')
        if vlan:
            vlan_pcp = vlan.pcp
            vlan_cfi = vlan.cfi
            vlan_vid = vlan.vid
            vlan_ethertype = vlan.ethertype
            if self.debug_pktin == 1:
                LOG.info("vlan_pcp:%s vlan_cfi:%s vlan_vid:%s vlan_ethertype:0x%04x\n",vlan_pcp,vlan_cfi,vlan_vid,vlan_ethertype)

        # IPv4 information
        ipv4 = self.find_protocol(pkt, 'ipv4')        
        if ipv4:
            ip_version = ipv4.version
            ip_header_length = ipv4.header_length
            ip_tos = ipv4.tos
            ip_total_length = ipv4.total_length
            ip_identification = ipv4.identification
            ip_flags = ipv4.flags
            ip_offset = ipv4.offset
            ip_ttl = ipv4.ttl
            #check the ttl
            if ip_ttl > 255:
                return
            ip_proto = ipv4.proto
            ip_csum = ipv4.csum
            #ip_src = socket.inet_ntoa(struct.pack('I',socket.htonl(ipv4.src)))
            ip_src = ipv4.src
            #ip_dst = socket.inet_ntoa(struct.pack('I',socket.htonl(ipv4.dst)))
            ip_dst = ipv4.dst
            ip_option = ipv4.option
            if self.debug_pktin == 1:
                LOG.info("ip_version:%s ip_header_length:%s tos:%s ip_total_length:%s",ip_version,ip_header_length,ip_tos,ip_total_length)
                LOG.info("ip_identification:%s ip_flags:%s ip_offset:%s ip_ttl:%s",ip_identification,ip_flags,ip_offset,ip_ttl)
                LOG.info("ip_proto:%s ip_csum:%s ip_src:%s ip_dst:%s",ip_proto,ip_csum,ip_src,ip_dst)
                LOG.info("ip_option:%s\n",ip_option)
            self.ipProcess(datapath, in_port, pkt, msg)

        # Arp information
        arp = self.find_protocol(pkt, 'arp')
        if arp:
            arp_hwtype = arp.hwtype
            arp_proto = arp.proto          
            arp_hlen = arp.hlen
            arp_plen = arp.plen
            arp_opcode = arp.opcode
            #arp_src_mac = haddr_to_str(arp.src_mac)
            arp_src_mac = arp.src_mac
            #arp_src_ip = socket.inet_ntoa(struct.pack('I',socket.htonl(arp.src_ip)))
            arp_src_ip = arp.src_ip
            #arp_dst_mac = haddr_to_str(arp.dst_mac)
            arp_dst_mac = arp.dst_mac
            #arp_dst_ip = socket.inet_ntoa(struct.pack('I',socket.htonl(arp.dst_ip)))
            arp_dst_ip = arp.dst_ip
            #arp_length = arp.length
            if self.debug_pktin == 1:
                LOG.info("arp_hwtype:%s arp_proto:%s arp_hlen:%s arp_plen:%s",arp_hwtype,arp_proto,arp_hlen,arp_plen)
                LOG.info("arp_opcode:%s arp_src_mac:%s arp_src_ip:%s arp_dst_mac:%s",arp_opcode,arp_src_mac,arp_src_ip,arp_dst_mac)
                LOG.info("arp_dst_ip:%s\n",arp_dst_ip)
            self.arpProcess(datapath, in_port, pkt, msg)

        # Tcp information
        tcp = self.find_protocol(pkt, 'tcp')
        if tcp:
            tcp_src_port = tcp.src_port
            tcp_dst_port = tcp.dst_port
            tcp_seq = tcp.seq
            tcp_ack = tcp.ack
            tcp_offset = tcp.offset
            tcp_bits = tcp.bits
            tcp_window_size = tcp.window_size
            tcp_csum = tcp.csum
            tcp_urgent = tcp.urgent
            #tcp_length = tcp.length 
            tcp_option = tcp.option
            if self.debug_pktin == 1:
                LOG.info("tcp_src_port:%s tcp_dst_port:%s tcp_seq:%s tcp_ack:%s",tcp_src_port,tcp_dst_port,tcp_seq,tcp_ack)
                LOG.info("tcp_offset:%s tcp_bits:%s tcp_window_size:%s tcp_csum:%s",tcp_offset,tcp_bits,tcp_window_size,tcp_csum)
                LOG.info("tcp_urgent:%s tcp_option:%s\n",tcp_urgent,tcp_option)

        # Udp information
        udp = self.find_protocol(pkt, 'udp')
        if udp:
            udp_src_port = udp.src_port
            udp_dst_port = udp.dst_port
            udp_total_length = udp.total_length
            udp_csum = udp.csum
            #upp_length = udp.length
            if self.debug_pktin == 1:
                LOG.info("udp_src_port:%s udp_dst_port:%s udp_total_length:%s",udp_src_port,udp_dst_port,udp_total_length)
                LOG.info("udp_csum:%s\n",udp_csum)

        # icmp information
        icmp = self.find_protocol(pkt, 'icmp')
        if icmp:
            icmp_type = icmp.type
            icmp_code = icmp.code
            icmp_csum = icmp.csum
            icmp_data = icmp.data
            if self.debug_pktin == 1:
                LOG.info("icmp_type:%s icmp_code:%s icmp_csum:%s icmp_data:%s\n",icmp_type,icmp_code,icmp_csum,icmp_data)
        #else:
            #LOG.info("unkown packets")                      #########the else has question
                        
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})
        pkt = packet.Packet(array.array('B', ev.msg.data))

        # get in_port information
        for f in msg.match.fields:
            print "f:%s\n" % f     
            if f.header == ofproto_v1_2.OXM_OF_IN_PORT:
                in_port = f.value
            if self.debug_pktin == 1:
                LOG.info("::::PacketIn in_port:%s\n", in_port)       

        #get the src, dst mac address
        mac_addr = self.find_protocol(pkt,'ethernet')
        if mac_addr:
            #print(mac_addr.src)
            #print(mac_addr.dst)
            #print(mac_addr.ethertype)
            #src = haddr_to_str(mac_addr.src)
            #dst = haddr_to_str(mac_addr.dst)
            #mac_ethertype = mac_addr.ethertype
            src = mac_addr.src
            dst = mac_addr.dst
            mac_ethertype = mac_addr.ethertype
        
        # flood l2 protocol packets.
        #dstmac = dst.split(':')     
        #if dstmac[0] == '01':
            #for m in self.vlan_table:
                #if in_port in self.vlan_table[m]:
                     #out_ports = self.vlan_table[m]
                     #break
            #output = out_ports
            #actions = []
            #if type(output) is ListType:
                #for outPort in output:
                    #actions.append(datapath.ofproto_parser.OFPActionOutput(outPort, 0))
            #elif type(output) is IntType:
                #actions.append(datapath.ofproto_parser.OFPActionOutput(output, 0))
            #out = datapath.ofproto_parser.OFPPacketOut(
                #datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port,
                #actions=actions)
            #datapath.send_msg(out)                   
            
        #learn a mac address and install host flow in switch.  
            self.mac_table[src] = in_port
            match = self.match_v12(datapath, dl_dst=src, dl_type=0x0800)
            actions = self.action_v12(datapath,out_port=in_port)
            self.flow_v12(datapath, priority=1500,table_id=0, match=match, flags=1, 
                           command=0, buffer_id=0xffffffff, actions=actions)

        #flood packets sent from local
        #if mac_ethertype == 0x8035:
        if in_port == 0xfffffffe:
            output = datapath.ofproto.OFPP_FLOOD
            actions = [datapath.ofproto_parser.OFPActionOutput(output,0)]
            out = datapath.ofproto_parser.OFPPacketOut(
                datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port,
                actions=actions)
            datapath.send_msg(out)
        
        # packet process
        else:
            if mac_ethertype == 0x0800 or mac_ethertype == 0x0806:
                self.packetProcess(datapath,in_port,pkt,msg)
            else:
                #flood un-ipv4 and un-arp
                for m in self.vlan_table.keys():
                    if in_port in self.vlan_table[m]:
                         out_ports = self.vlan_table[m]
                         break
                output = out_ports
                actions = []
                if type(output) is ListType:
                    for outPort in output:
                        actions.append(datapath.ofproto_parser.OFPActionOutput(outPort, 0))
                elif type(output) is IntType:
                    actions.append(datapath.ofproto_parser.OFPActionOutput(output, 0))
                out = datapath.ofproto_parser.OFPPacketOut(
                    datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port,
                    actions=actions)
                datapath.send_msg(out)                   

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def _port_status_handler(self, ev):
        msg = ev.msg
        #self.dir_print(msg)
        #self.dir_print(msg.desc)
        reason = msg.reason
        port_no = msg.desc.port_no

        ofproto = msg.datapath.ofproto
        if reason == ofproto.OFPPR_ADD:
            LOG.info("port added %s", port_no)
        elif reason == ofproto.OFPPR_DELETE:
            LOG.info("port deleted %s", port_no)
        elif reason == ofproto.OFPPR_MODIFY:
            LOG.info("port modified %s", port_no)
        else:
            LOG.info("Illeagal port state %s %s", port_no, reason)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        LOG.info("::::Initial the switch")
        time.sleep(3)
        LOG.info("::::Install some flow for default route and connect route")
        self.installDefaultFlow(datapath)
        time.sleep(2)
        LOG.info("::::Finished install flows")
        
