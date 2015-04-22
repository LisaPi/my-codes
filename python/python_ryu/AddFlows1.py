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


class AddFlow(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_2.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(AddFlow, self).__init__(*args, **kwargs)
        self.mac_to_port = {} 

    inport = 1
    output = 3
    vlanid = 1
       
    #install the 1024 defalt flows
    def installDefaultFlow(self,datapath):
        #match = self.match_v12(datapath,in_port=self.inport)
        #actions = self.action_v12(datapath, out_port=self.output)
        #self.flow_v12(datapath, match=match,actions=actions)
        match = self.match_v12(datapath)
        actions = self.action_v12(datapath)
        self.flow_v12(datapath, priority=1,match=match,actions=actions)

    def installFlow(self,datapath):
        match = self.match_v12(datapath,in_port=self.inport,vlan_vid=self.vlanid)
        actions = self.action_v12(datapath, out_port=self.output)
        self.flow_v12(datapath, priority=100,match=match,actions=actions)
                 
    def removeFlow(self,datapath):
        #remove controller flow
        match_del = self.match_v12(datapath,in_port=self.inport)
        self.flow_v12(datapath, table_id=0, flags=1, match=match_del, command=3)

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

    def dir_print(self, msg):
        print "%s\n" % dir(msg)
 
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
        LOG.info("::::Instal a drop flow")
        #self.installDefaultFlow(datapath)
        #time.sleep(5)
        #LOG.info("::::Wait 10s to delete flows")
        #for i in range(1,10):
        while 1:
            for self.vlanid in range(1,1024):
                self.installFlow(datapath)
            print("has add 1024 flows")
            time.sleep(15)
            self.removeFlow(datapath)
            print("has delete all")
            time.sleep(10)
        #LOG.info("::::Instal and delete flow ok")
            
