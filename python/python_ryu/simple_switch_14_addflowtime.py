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
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_4
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
LOG = logging.getLogger('ryu.app.simple_switch')
import time
class SimpleSwitch14(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_4.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch14, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

    cnt = 0
    packetArr = []

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.
        #for j in range(1, 3):
        #    for i in range(0, 256):  
        #        ip_dst='192.168.%d.%d'%(j,i)
        #        match = parser.OFPMatch(eth_type=0x0800,ipv4_dst=ip_dst)
        #        actions = [parser.OFPActionOutput(22,
        #                                  ofproto.OFPCML_NO_BUFFER)]
        #        self.add_flow(datapath, 0, match, actions)
        LOG.info("please send packets")          
        time.sleep(30)
        for j in range(1, 2):
            for i in range(0, 256):  
                ip_dst='192.168.%d.%d'%(j,i)
                match = parser.OFPMatch(eth_type=0x0800,ipv4_dst=ip_dst)
                actions = [parser.OFPActionOutput(22,
                                          ofproto.OFPCML_NO_BUFFER)]
                self.add_flow(datapath, 0, match, actions)
        LOG.info("output:22")
        #time.sleep(30)
        for j in range(1, 2):
            for i in range(0, 256):
                #vlan=j
                ip_src='192.169.%d.%d'%(j,i)
                match = parser.OFPMatch(eth_type=0x0800,ipv4_src=ip_src)
                actions = [parser.OFPActionOutput(23,
                                          ofproto.OFPCML_NO_BUFFER)]       
                self.add_flow(datapath, 2, match, actions)
        LOG.info("output:23")
        #match = parser.OFPMatch()
        #actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
        #                                  ofproto.OFPCML_NO_BUFFER)]
        #self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        datapath.send_msg(mod)
    
    #@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    #def _packet_in_handler(self, ev):
    #    msg = ev.msg
    #    datapath = msg.datapath
    #    ofproto = datapath.ofproto
    #    #parser = datapath.ofproto_parser
    #    self.cnt += 1
    #    LOG.info("has receive %s packets", self.cnt)
       
