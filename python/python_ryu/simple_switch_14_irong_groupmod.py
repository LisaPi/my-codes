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

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_4
from ryu.ofproto import ofproto_v1_4_parser
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet

from types import *
from ryu.controller import handler
from ryu.controller import mac_to_port
from ryu.ofproto import ether
from ryu.lib.mac import haddr_to_str
from ryu.lib.packet import *
from ryu.lib.packet import arp
from ryu.lib.packet import icmp
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp
from ryu.lib.packet import udp
from ryu.lib.packet import vlan
from ryu.lib import mac


class SimpleSwitch14(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_4.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch14, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        match = parser.OFPMatch()

        #src = "22:00:00:00:00:00"
        #action = [datapath.ofproto_parser.OFPActionSetField(eth_src=src), ]
        #actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
        #                                   ofproto.OFPCML_NO_BUFFER)]
        #actions.extend(action)
        
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                           ofproto.OFPCML_NO_BUFFER)]

        #self.send_role_request(datapath)
        #self.send_rol_req(datapath) 
        #self.send_set_async(datapath)
        self.add_flow(datapath, 1, match, actions)
        

    def send_set_async(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        properties = []
        property = [ofp_parser.OFPAsyncConfigPropReasons(
                              11, 3000,3)]
        properties.extend(property)
        #property = [ofp_parser.OFPAsyncConfigPropReasons(
        #                      10, 2000,1)]
        #properties.extend(property)
        
        req = ofp_parser.OFPSetAsync(datapath, properties)
        datapath.send_msg(req)
        
        self.send_get_async_request(datapath)

    def send_get_async_request(self, datapath):
        ofp_parser = datapath.ofproto_parser

        req = ofp_parser.OFPGetAsyncRequest(datapath)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPGetAsyncReply, MAIN_DISPATCHER)
    def get_async_reply_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath

        self.logger.debug('OFPGetAsyncReply received: '
                              'properties=%s', repr(msg.properties))       
      
    def send_role_request(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        req = ofp_parser.OFPRoleRequest(datapath, ofp.OFPCR_ROLE_SLAVE, 0)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPRoleReply, MAIN_DISPATCHER)
    def role_reply_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofp = datapath.ofproto

        if msg.role == ofp.OFPCR_ROLE_NOCHANGE:
            role = 'NOCHANGE'
        elif msg.role == ofp.OFPCR_ROLE_EQUAL:
            role = 'EQUAL'
        elif msg.role == ofp.OFPCR_ROLE_MASTER:
            role = 'MASTER'
        elif msg.role == ofp.OFPCR_ROLE_SLAVE:
            role = 'SLAVE'
        else:
            role = 'unknown'

        self.logger.debug('OFPRoleReply received: '
                      'role=%s generation_id=%d',
                      role, msg.generation_id)

       

    def send_rol_req(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        req = ofp_parser.OFPRoleRequest(datapath, ofp.OFPCR_ROLE_MASTER, 0)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPRoleReply, MAIN_DISPATCHER)
    def role_reply_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofp = datapath.ofproto

        if msg.role == ofp.OFPCR_ROLE_NOCHANGE:
            role = 'NOCHANGE'
        elif msg.role == ofp.OFPCR_ROLE_EQUAL:
            role = 'EQUAL'
        elif msg.role == ofp.OFPCR_ROLE_MASTER:
            role = 'MASTER'
        elif msg.role == ofp.OFPCR_ROLE_SLAVE:
            role = 'SLAVE'
        else:
            role = 'unknown'

        self.logger.debug('OFPRoleReply received: '
                      'role=%s generation_id=%d',
                      role, msg.generation_id)


    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        datapath.send_msg(mod)

        time.sleep(5)

        #create group 55
        buckets = []
        buckets = [datapath.ofproto_parser.OFPActionOutput(2, 0)]
        #buckets = [datapath.ofproto_parser.OFPActionOutput(0xfffffffd, 0)]
        buckets = self.bucket_v12(datapath, action=buckets)
        #bucket_output_49 = [datapath.ofproto_parser.OFPActionOutput(49, 0)]
        #bucket_49 = self.bucket_v12(datapath, action=bucket_output_49)
        #buckets.extend(bucket_49)
        
        self.group_v12(datapath, command=0, type_=datapath.ofproto.OFPGT_INDIRECT, groupid=1, buckets=buckets)

        #match = self.match_v12(datapath, dl_type=0x0800)
        #actions = self.action_v12(datapath,actions=[datapath.ofproto_parser.OFPActionGroup(1,datapath.ofproto.OFPGT_INDIRECT)])   
        #self.flow_v12(datapath, priority=20, table_id=0, match=match, flags=1, 
        #               command=0, buffer_id=0xffffffff, actions=actions) 

    def bucket_v12(self, datapath, len_=0, weight=0, watch_port=0xffffffff, watch_group=0xffffffff,action=[]):
        buckets = [datapath.ofproto_parser.OFPBucket(len_=len_, weight=weight, watch_port=watch_port,watch_group=watch_group, actions=action)]
        return buckets

    def group_v12(self, datapath, command=0, type_=0, groupid=0, buckets=None):
        group = datapath.ofproto_parser.OFPGroupMod(datapath=datapath,command=command,type_=type_, group_id=groupid, buckets=buckets)
        datapath.send_msg(group)
        
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            self.add_flow(datapath, 1, match, actions)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
