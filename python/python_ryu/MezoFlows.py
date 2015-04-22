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


class MezoFlow(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_2.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(MezoFlow, self).__init__(*args, **kwargs)
        self.mac_to_port = {} 

    #Configure MAC address
    nextmac_dst = '00:25:90:9b:b8:38'
    
    #ip_table = ['10.0.0.5','10.0.0.6','10.0.0.7','10.0.0.8',]
    port_table= {'1':['10.0.0.1','10.0.0.41'], '2':['10.0.0.2','10.0.0.42'], 
                        '5':['10.0.0.5','10.0.0.53'],
                        '6':['10.0.0.6','10.0.0.54']}
    flowList = [[6, '10.0.0.6'], [48, '10.0.0.148'], [48, '10.0.0.131'],
        [48, '10.0.0.188'],[48, '10.0.0.155'],
        [48, '10.0.0.147'],[48, '10.0.0.164'],[24, '10.0.0.24'],
        [48, '10.0.0.143'],[48, '10.0.0.177'],[48, '10.0.0.176'],
        [30, '10.0.0.30'],[48, '10.0.0.149'],[29, '10.0.0.29'],
        [4, '10.0.0.4'],[36, '10.0.0.36'],[48, '10.0.0.154'],
        [48, '10.0.0.129'],[21, '10.0.0.21'],[11, '10.0.0.11'],
        [48, '10.0.0.175'],[48, '10.0.0.166'],[13, '10.0.0.13'],
        [48, '10.0.0.169'],[48, '10.0.0.156'],[3, '10.0.0.3'],
        [38, '10.0.0.38'],[48, '10.0.0.151'],[48, '10.0.0.180'],
        [48, '10.0.0.137'],[48, '10.0.0.174'],[48, '10.0.0.161'],
        [25, '10.0.0.25'],[48, '10.0.0.163'],[28, '10.0.0.28'],
        [48, '10.0.0.138'],[48, '10.0.0.141'],[2, '10.0.0.2'],
        [48, '10.0.0.144'],[48, '10.0.0.182'],[8, '10.0.0.8'],
        [7, '10.0.0.7'],[48, '10.0.0.189'],[48, '10.0.0.187'],
        [48, '10.0.0.186'],[48, '10.0.0.165'],[48, '10.0.0.132'],
        [48, '10.0.0.184'],[48, '10.0.0.136'],[48, '10.0.0.145'],
        [48, '10.0.0.158'],[35, '10.0.0.35'],[20, '10.0.0.20'],
        [12, '10.0.0.12'],[40, '10.0.0.40'],[48, '10.0.0.178'],
        [48, '10.0.0.179'],[31, '10.0.0.31'],[48, '10.0.0.135'],
        [48, '10.0.0.152'],[48, '10.0.0.190'],[48, '10.0.0.181'],
        [48, '10.0.0.167'],[48, '10.0.0.130'],[48, '10.0.0.142'],
        [48, '10.0.0.173'],[48, '10.0.0.168'],[48, '10.0.0.153'],
        [9, '10.0.0.9'],[48, '10.0.0.160'],[32, '10.0.0.32'],
        [48, '10.0.0.170'],[48, '10.0.0.157'],[48, '10.0.0.133'],
        [15, '10.0.0.15'],[23, '10.0.0.23'],[22, '10.0.0.22'],
        [16, '10.0.0.16'],[48, '10.0.0.150'],[48, '10.0.0.159'],
        [48, '10.0.0.134'],[14, '10.0.0.14'],[48, '10.0.0.139'],
        [39, '10.0.0.39'],[10, '10.0.0.10'],[34, '10.0.0.34'],
        [48, '10.0.0.140'],[48, '10.0.0.146'],[48, '10.0.0.162'],
        [26, '10.0.0.26'],[48, '10.0.0.185'],[48, '10.0.0.171'],
        [27, '10.0.0.27'],[1, '10.0.0.1'],[33, '10.0.0.33'],
        [18, '10.0.0.18'],[48, '10.0.0.172'],[17, '10.0.0.17'],
        [48, '10.0.0.183'],[19, '10.0.0.19'],[37, '10.0.0.37'],
        [1, '10.0.0.61'],[2, '10.0.0.62'],[3, '10.0.0.63'],
        [4, '10.0.0.64'],[5, '10.0.0.5'],[5, '10.0.0.65'],
        [6, '10.0.0.66'],[7, '10.0.0.67'],[8, '10.0.0.68'],
        [9, '10.0.0.69'],[10, '10.0.0.70'],[11, '10.0.0.71'],
        [12, '10.0.0.72'],[13, '10.0.0.73'],[14, '10.0.0.74'],
        [15, '10.0.0.75'],[16, '10.0.0.76'],[17, '10.0.0.77'],
        [18, '10.0.0.78'],[19, '10.0.0.79'],[20, '10.0.0.80'],
        [21, '10.0.0.81'],[22, '10.0.0.82'],[23, '10.0.0.83'],
        [24, '10.0.0.84'],[25, '10.0.0.85'],[26, '10.0.0.86'],
        [27, '10.0.0.87'],[28, '10.0.0.88'],[29, '10.0.0.89'],
        [30, '10.0.0.90'],[31, '10.0.0.91'],[32, '10.0.0.92'],
        [33, '10.0.0.93'],[34, '10.0.0.94'],[35, '10.0.0.95'],
        [36, '10.0.0.96'],[37, '10.0.0.97'],[38, '10.0.0.98'],
        [39, '10.0.0.99'],[40, '10.0.0.100']]
     
    #install the defalt flow according the route table
    def installDefaultFlow(self,datapath):
        #create fixed flows
        #50000 ipv6 actions=drop
        for lType in {0x86dd, 0x8035, 0x8809, 0x2000, 0x8100}:
            match = self.match_v12(datapath,dl_type=lType)
            actions = []
            self.flow_v12(datapath, priority=50000, match=match,actions=actions)

        #50000 ip nw_src=10.0.0.128/25 nw_dst=10.0.0.128/25 actions=drop
        match = self.match_v12(datapath,dl_type=0x0800,ipv4_src='10.0.0.128', 
                           ipv4_src_mask='255.255.255.128', ipv4_dst='10.0.0.128',ipv4_dst_mask='255.255.255.128')
        actions = []
        self.flow_v12(datapath, priority=50000, match=match,actions=actions)

        #40000 udp nw_dst=255.255.255.255 tp_dst=67 actions=CONTROLLER:1024
        match = self.match_v12(datapath,dl_type=0x0800,ip_proto=17, ipv4_dst='255.255.255.255')
        actions = []
        actions.append(datapath.ofproto_parser.OFPActionOutput(datapath.ofproto.OFPP_CONTROLLER, 1024))
        self.flow_v12(datapath, priority=40000, match=match,actions=actions)

        #100 ip in_port=49 nw_dst=10.0.0.0/22   actions=drop
        #100 ip in_port=50 nw_dst=10.0.0.0/22   actions=drop
        #100 ip in_port=51 nw_dst=10.0.0.0/22   actions=drop
        #100 ip in_port=52 nw_dst=10.0.0.0/22   actions=drop
        for port in {49, 50, 51, 52}:
            match = self.match_v12(datapath,dl_type=0x0800, ipv4_dst='10.0.0.0',ipv4_dst_mask='255.255.252.0')
            actions = []
            self.flow_v12(datapath, priority=100, match=match,actions=actions)

        #5 ip actions=drop
        match = self.match_v12(datapath,dl_type=0x0800)
        actions = []
        self.flow_v12(datapath, priority=5, match=match,actions=actions)

        #40000 in_port=52 dl_type=0x88b5 actions=CONTROLLER:1024
        #40000 in_port=49 dl_type=0x88b5 actions=CONTROLLER:1024
        #40000 in_port=50 dl_type=0x88b5 actions=CONTROLLER:1024
        #40000 in_port=51 dl_type=0x88b5 actions=CONTROLLER:1024
        for port in {49, 50, 51, 52}:
            match = self.match_v12(datapath,in_port=port, dl_type=0x88b5)
            actions = []
            actions.append(datapath.ofproto_parser.OFPActionOutput(datapath.ofproto.OFPP_CONTROLLER, 1024))
            self.flow_v12(datapath, priority=40000, match=match,actions=actions)

        #40000 ip in_port=6 nw_src=10.0.0.6 actions=CONTROLLER:1024
        #.............
        #40000 ip in_port=37 nw_src=10.0.0.37  actions=CONTROLLER:1024
        #flowList = [[48,'10.0.0.148'],[48,'10.0.0.131'],[48,'10.0.0.188']]
        
        for flow in self.flowList:
            match = self.match_v12(datapath,in_port=flow[0], ipv4_src=flow[1], dl_type=0x0800)
            actions = []
            actions.append(datapath.ofproto_parser.OFPActionOutput(datapath.ofproto.OFPP_CONTROLLER, 1024))
            self.flow_v12(datapath, priority=40000, match=match,actions=actions)
        
        #create group 55
        buckets = []
        bucket_output_49 = [datapath.ofproto_parser.OFPActionOutput(49, 0)]
        bucket_49 = self.bucket_v12(datapath, weight=1, action=bucket_output_49)
        buckets.extend(bucket_49)
        bucket_output_50 = [datapath.ofproto_parser.OFPActionOutput(50, 0)]
        bucket_50 = self.bucket_v12(datapath, weight=1, action=bucket_output_50)
        buckets.extend(bucket_50)
        bucket_output_51 = [datapath.ofproto_parser.OFPActionOutput(51, 0)]
        bucket_51 = self.bucket_v12(datapath, weight=1, action=bucket_output_51)
        buckets.extend(bucket_51)
        bucket_output_52 = [datapath.ofproto_parser.OFPActionOutput(52, 0)]
        bucket_52 = self.bucket_v12(datapath, weight=1, action=bucket_output_52)
        buckets.extend(bucket_52)
        
        self.group_v12(datapath, command=0, type_=datapath.ofproto.OFPGT_SELECT, groupid=56, buckets=buckets)
        
        #get the ip and install the flows

        #get the packets info and install the new flow rules

    #def installFlowRules(self, datapath, in_port, src, ip_src, pkt, msg):
    def installFlowRules(self, datapath, in_port, src, ip_src):
        #for port in self.port_table.keys(): 
        port = str(in_port)
        dstmac = '00:25:90:c0:bc:3e'
        output = 3
        #if port in self.port_table:
            #install the flows
        print('############')
            #for index in [0,1]:
            #if ip_src in self.port_table[port]:
                #match = self.match_v12(datapath, dl_type=0x0806, arp_tpa=self.port_table[port][index])
        match = self.match_v12(datapath, dl_type=0x0806, arp_tpa=ip_src)
        actions = self.action_v12(datapath,dl_dst=src,
                                        out_port=int(port))
        self.flow_v12(datapath, priority=30000, table_id=0, match=match, flags=1, 
                       command=0, buffer_id=0xffffffff, actions=actions)
        LOG.info(":::Add arp flow")
                
            #for index in [0,1]:
            #if ip_src in self.port_table[port]:
                #match = self.match_v12(datapath, in_port=48, dl_type=0x0800,  ipv4_src='10.0.0.128', ipv4_src_mask='255.255.255.128', ipv4_dst=self.port_table[port][index])
        match = self.match_v12(datapath, in_port=48, dl_type=0x0800,  ipv4_src='10.0.0.128', ipv4_src_mask='255.255.255.128', ipv4_dst=ip_src)
        actions = self.action_v12(datapath,dl_dst=src, out_port=int(port))                
        self.flow_v12(datapath, priority=20000, table_id=0, match=match, flags=1, command=0, buffer_id=0xffffffff, actions=actions)

            #for index in [0,1]:
            #if ip_src in self.port_table[port]:
                #match = self.match_v12(datapath, dl_type=0x0800, ipv4_src='10.0.0.0', ipv4_src_mask='255.255.255.128', ipv4_dst=self.port_table[port][index])
        match = self.match_v12(datapath, dl_type=0x0800, ipv4_src='10.0.0.0', ipv4_src_mask='255.255.255.128', ipv4_dst=ip_src)
        actions = self.action_v12(datapath,dl_dst=src, out_port=int(port))
        self.flow_v12(datapath, priority=20000, table_id=0, match=match, flags=1, command=0, buffer_id=0xffffffff, actions=actions)

            #for index in [0,1]:
            #if ip_src in self.port_table[port]:
                #match = self.match_v12(datapath, in_port=49,dl_type=0x0800, ipv4_dst=self.port_table[port][index])
        match = self.match_v12(datapath, in_port=49,dl_type=0x0800, ipv4_dst=ip_src)
        actions = self.action_v12(datapath,dl_dst=src, out_port=int(port))               
        self.flow_v12(datapath, priority=10000, table_id=0, match=match, flags=1, 
                           command=0, buffer_id=0xffffffff, actions=actions)

            #for index in [0,1]:
            #if ip_src in self.port_table[port]:
                #match = self.match_v12(datapath, in_port=50,dl_type=0x0800, ipv4_dst=self.port_table[port][index])
        match = self.match_v12(datapath, in_port=50,dl_type=0x0800, ipv4_dst=ip_src)
        actions = self.action_v12(datapath,dl_dst=src, out_port=int(port))               
        self.flow_v12(datapath, priority=10000, table_id=0, match=match, flags=1, 
                       command=0, buffer_id=0xffffffff, actions=actions)

            #for index in [0,1]:
            #if ip_src in self.port_table[port]:
                #match = self.match_v12(datapath, in_port=51,dl_type=0x0800, ipv4_dst=self.port_table[port][index])
        match = self.match_v12(datapath, in_port=51,dl_type=0x0800, ipv4_dst=ip_src)
        actions = self.action_v12(datapath,dl_dst=src, out_port=int(port))               
        self.flow_v12(datapath, priority=10000, table_id=0, match=match, flags=1, 
                           command=0, buffer_id=0xffffffff, actions=actions)

            #for index in [0,1]:
            #if ip_src in self.port_table[port]:
                #match = self.match_v12(datapath, in_port=52,dl_type=0x0800, ipv4_dst=self.port_table[port][index])
        match = self.match_v12(datapath, in_port=52,dl_type=0x0800, ipv4_dst=ip_src)
        actions = self.action_v12(datapath,dl_dst=src, out_port=int(port))               
        self.flow_v12(datapath, priority=10000, table_id=0, match=match, flags=1, 
                           command=0, buffer_id=0xffffffff, actions=actions)

            #for index in [0,1]:
            #if ip_src in self.port_table[port]:
                #match = self.match_v12(datapath, dl_type=0x0800, ipv4_src=self.port_table[port][index] )
        match = self.match_v12(datapath, dl_type=0x0800, ipv4_src=ip_src)
        actions = self.action_v12(datapath,dl_dst=dstmac, out_port=output)  
        self.flow_v12(datapath, priority=10, table_id=0, match=match, flags=1, 
                       command=0, buffer_id=0xffffffff, actions=actions) 

            #for index in [0,1]:
            #if ip_src in self.port_table[port]:
                #match = self.match_v12(datapath, dl_type=0x0800, ipv4_src=self.port_table[port][index], ipv4_dst='10.0.0.0',ipv4_dst_mask='255.0.0.0')
        match = self.match_v12(datapath, dl_type=0x0800, ipv4_src=ip_src, ipv4_dst='10.0.0.0',ipv4_dst_mask='255.0.0.0')
        actions = self.action_v12(datapath,actions=[datapath.ofproto_parser.OFPActionGroup(56,datapath.ofproto.OFPGT_SELECT)])   
        self.flow_v12(datapath, priority=20, table_id=0, match=match, flags=1, 
                       command=0, buffer_id=0xffffffff, actions=actions)  

        #remove controller flow
        match_del = self.match_v12(datapath,in_port=in_port, dl_type=0x0800,ipv4_src=ip_src)
        self.flow_v12(datapath, table_id=0, flags=1, match=match_del, command=3)


    def bucket_v12(self, datapath, len_=0, weight=0, watch_port=0, watch_group=0,action=[]):
        buckets = [datapath.ofproto_parser.OFPBucket(len_=len_, weight=weight, watch_port=watch_port,watch_group=watch_group, actions=action)]
        return buckets

    def group_v12(self, datapath, command=0, type_=0, groupid=0, buckets=None):
        group = datapath.ofproto_parser.OFPGroupMod(datapath=datapath,command=command,type_=type_, group_id=groupid, buckets=buckets)
        datapath.send_msg(group)


    def match_v12(self, datapath, in_port=None, dl_dst=None, dl_src=None, dl_type=None, 
                 vlan_vid=None, vlan_pcp=None, ip_dscp=None, ip_ecn=None, ip_proto=None, ipv4_src=None, 
                 ipv4_src_mask=None, ipv4_dst=None, ipv4_dst_mask=None, tcp_src=None, tcp_dst=None, 
                 udp_src=None, udp_dst=None, arp_tpa=None):
                 
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
            match.set_ipv4_src_masked(ipv4_src, ipv4_src_mask)
            
        if ipv4_dst is not None:
            ipv4_dst = self.ipv4_to_int(ipv4_dst)
            match.set_ipv4_dst(ipv4_dst)

        if ipv4_dst_mask is not None:
            ipv4_dst_mask = self.ipv4_to_int(ipv4_dst_mask)
            match.set_ipv4_dst_masked(ipv4_dst, ipv4_dst_mask)

        if tcp_src is not None:
            match.set_tcp_src(tcp_src)
            
        if tcp_dst is not None:
            match.set_tcp_dst(tcp_dst)
            
        if udp_src is not None:
            match.set_udp_src(udp_src)
            
        if udp_dst is not None:
            match.set_udp_dst(udp_dst)
            
        if arp_tpa is not None:
            arp_tpa = self.ipv4_to_int(arp_tpa)
            match.set_arp_tpa(arp_tpa)
            
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
        #else:
            #actions.append(datapath.ofproto_parser.OFPActionOutput(datapath.ofproto.OFPP_ALL, 0))
       
        return actions


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
            
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})
 
        # get in_port information
        for f in msg.match.fields:
            print "f:%s\n" % f
            if f.header == ofproto_v1_2.OXM_OF_IN_PORT:
                in_port = f.value
 
        LOG.info("\n########Packet_in from port: ########")
        LOG.info("in_port:%s\n", in_port)
 
        # packet information (primary packets: LOG.info("packets:%s", pkt.protocols))
        pkt = packet.Packet(array.array('B', ev.msg.data))
        #self.packet_print(pkt)
 
        # get the src, dst mac address
        mac_addr = self.find_protocol(pkt,'ethernet')
        if mac_addr:
            #src = haddr_to_str(mac_addr.src)
            #dst = haddr_to_str(mac_addr.dst)
            src = mac_addr.src
            dst = mac_addr.dst
 
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
            ip_proto = ipv4.proto
            ip_csum = ipv4.csum
            #ip_src = socket.inet_ntoa(struct.pack('I',socket.htonl(ipv4.src)))
            #ip_dst = socket.inet_ntoa(struct.pack('I',socket.htonl(ipv4.dst)))
            ip_src = ipv4.src
            ip_dst = ipv4.dst
            #ip_length = ipv4.length
            ip_option = ipv4.option
            LOG.info("########Find a new server and try to install flows########")
            LOG.info("ip_proto:%s ip_src:%s ip_dst:%s",ip_proto,ip_src,ip_dst)
            # Call the function to install the flows for each server
            iplist = [int(in_port), ip_src]
            if iplist in self.flowList:
                self.installFlowRules(datapath, in_port, src, ip_src)
 
        # Arp information
        arp = self.find_protocol(pkt, 'arp')
        if arp:
            arp_hwtype = arp.hwtype
            arp_proto = arp.proto
            arp_hlen = arp.hlen
            arp_plen = arp.plen
            arp_opcode = arp.opcode
            #arp_src_mac = haddr_to_str(arp.src_mac)
            #arp_src_ip = socket.inet_ntoa(struct.pack('I',socket.htonl(arp.src_ip)))
            #arp_dst_mac = haddr_to_str(arp.dst_mac)
            #arp_dst_ip = socket.inet_ntoa(struct.pack('I',socket.htonl(arp.src_ip)))
            arp_src_mac = arp.src_mac
            arp_src_ip = arp.src_ip
            arp_dst_mac = arp.dst_mac
            arp_dst_ip = arp.src_ip
            #arp_length = arp.length
            LOG.info("########Find a new server and try to install flows########")
            LOG.info("arp_opcode:%s arp_src_mac:%s arp_src_ip:%s arp_dst_mac:%s",arp_opcode,arp_src_mac,arp_src_ip,arp_dst_mac)
            # Call the function to install the flows for each server
            iplist = [int(in_port), arp_src_ip]
            if iplist in self.flowList:
                self.installFlowRules(datapath, in_port, src, arp_src_ip)
            
 
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
        time.sleep(5)
        LOG.info("::::Install flows actions=controller")
        self.installDefaultFlow(datapath)
        time.sleep(20)
        LOG.info("::::Finished install flows")
        
