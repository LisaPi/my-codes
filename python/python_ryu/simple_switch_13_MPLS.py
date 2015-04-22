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

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
import time


class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

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
        #match = parser.OFPMatch(eth_dst='00:01:02:03:04:05', eth_src='00:06:07:08:09:0a', eth_type=0x8847,mpls_label=10)
        match = parser.OFPMatch(in_phy_port=1,eth_dst='00:01:02:03:04:05', eth_src='00:06:07:08:09:0a')
        actions1 = [parser.OFPActionOutput(ofproto.OFPP_ALL,
                                          ofproto.OFPCML_NO_BUFFER)]
        #actions2 = [parser.OFPActionDecMplsTtl()]
        actions3 = [parser.OFPActionPushMpls()]
        actions4 = [parser.OFPActionSetField(mpls_label=10)]
        actions = []
        actions.extend(actions3)
        actions.extend(actions4)
        #actions.extend(actions2)
        actions.extend(actions1)
        time.sleep(10)
        self.add_flow(datapath, 1000, match, ofproto.OFPP_ANY, ofproto.OFPG_ANY,actions)
        print("add push_mpls flow ok!")

        match = parser.OFPMatch(eth_type=0x8847)
        actions1 = [parser.OFPActionOutput(2,
                                          ofproto.OFPCML_NO_BUFFER)]
        #actions2 = [parser.OFPActionDecMplsTtl()]
        actions3 = [parser.OFPActionCopyTtlOut()]
        actions = []
        actions.extend(actions3)
        actions.extend(actions1)
        time.sleep(10)
        self.add_flow(datapath, 1000, match, ofproto.OFPP_ANY, ofproto.OFPG_ANY,actions)
        print("add copy ttl out flow ok!")

        match = parser.OFPMatch(eth_type=0x8847)
        actions1 = [parser.OFPActionOutput(2,
                                          ofproto.OFPCML_NO_BUFFER)]
        #actions2 = [parser.OFPActionDecMplsTtl()]
        actions3 = [parser.OFPActionCopyTtlOut()]
        actions = []
        actions.extend(actions3)
        actions.extend(actions1)
        time.sleep(10)
        self.add_flow(datapath, 1000, match, ofproto.OFPP_ANY, ofproto.OFPG_ANY,actions)
        print("add copy ttl out flow ok!")

        match = parser.OFPMatch(eth_type=0x8847)
        actions1 = [parser.OFPActionOutput(2,
                                          ofproto.OFPCML_NO_BUFFER)]
        #actions2 = [parser.OFPActionDecMplsTtl()]
        actions3 = [parser.OFPActionCopyTtlIn()]
        actions = []
        actions.extend(actions3)
        actions.extend(actions1)
        time.sleep(10)
        self.add_flow(datapath, 1000, match, ofproto.OFPP_ANY, ofproto.OFPG_ANY,actions)
        print("add copy ttl in flow ok!")

        match = parser.OFPMatch(in_phy_port=1,eth_dst='20:01:02:03:04:05', eth_src='20:06:07:08:09:0a')
        actions = []
        actions2 = [parser.OFPActionDecNwTtl()]
        actions.extend(actions2)
        actions1 = [parser.OFPActionOutput(ofproto.OFPP_ALL,
                                          ofproto.OFPCML_NO_BUFFER)]
        actions.extend(actions1)
        time.sleep(10)
        self.add_flow(datapath, 1000, match, ofproto.OFPP_ANY, ofproto.OFPG_ANY,actions)
        print("add dec_ttl flow ok!")      

        match = parser.OFPMatch(eth_type=0x86dd,ip_proto=6,ip_dscp=8)
        actions = []
        actions1 = [parser.OFPActionSetField(ip_dscp=16)]
        actions.extend(actions1)
        actions2 = [parser.OFPActionOutput(2,
                                          ofproto.OFPCML_NO_BUFFER)]
        actions.extend(actions2)
        time.sleep(10)
        self.add_flow(datapath, 1000, match, ofproto.OFPP_ANY, ofproto.OFPG_ANY,actions)
        print("add modify ip_dscp flow ok!")    

        match = parser.OFPMatch(eth_type=0x0800)
        actions = []
        actions1 = [parser.OFPActionPushVlan()]
        actions.extend(actions1)
        actions2 = [parser.OFPActionOutput(2,
                                          ofproto.OFPCML_NO_BUFFER)]
        actions.extend(actions2)
        time.sleep(10)
        self.add_flow(datapath, 1000, match, ofproto.OFPP_ANY, ofproto.OFPG_ANY,actions)
        print("add push_vlan flow ok!")    

        match = parser.OFPMatch(eth_type=0x86dd)
        actions = []
        actions1 = [parser.OFPActionPushVlan()]
        actions.extend(actions1)
        actions2 = [parser.OFPActionOutput(2,
                                          ofproto.OFPCML_NO_BUFFER)]
        actions.extend(actions2)
        time.sleep(10)
        self.add_flow(datapath, 1000, match, ofproto.OFPP_ANY, ofproto.OFPG_ANY,actions)
        print("ipv6 add push_vlan flow ok!")    

        match = parser.OFPMatch(eth_type=0x0806)
        actions = []
        actions1 = [parser.OFPActionPushVlan()]
        actions.extend(actions1)
        actions2 = [parser.OFPActionOutput(2,
                                          ofproto.OFPCML_NO_BUFFER)]
        actions.extend(actions2)
        time.sleep(10)
        self.add_flow(datapath, 1000, match, ofproto.OFPP_ANY, ofproto.OFPG_ANY,actions)
        print("ipv6 add push_vlan flow ok!")    

        match = parser.OFPMatch(eth_type=0x0800)
        actions = []
        actions1 = [parser.OFPActionPushVlan(ethertype=0x88a8)]
        actions.extend(actions1)
        actions2 = [parser.OFPActionOutput(2,
                                          ofproto.OFPCML_NO_BUFFER)]
        actions.extend(actions2)
        time.sleep(10)
        self.add_flow(datapath, 1000, match, ofproto.OFPP_ANY, ofproto.OFPG_ANY,actions)
        print("add push_vlan flow ok!")    

        match = parser.OFPMatch(eth_type=0x86dd)
        actions = []
        actions1 = [parser.OFPActionPushVlan(ethertype=0x88a8)]
        actions.extend(actions1)
        actions2 = [parser.OFPActionOutput(2,
                                          ofproto.OFPCML_NO_BUFFER)]
        actions.extend(actions2)
        time.sleep(10)
        self.add_flow(datapath, 1000, match, ofproto.OFPP_ANY, ofproto.OFPG_ANY,actions)
        print("ipv6 add push_vlan flow ok!")    

        match = parser.OFPMatch(eth_type=0x0806)
        actions = []
        actions1 = [parser.OFPActionPushVlan(ethertype=0x88a8)]
        actions.extend(actions1)
        actions2 = [parser.OFPActionOutput(2,
                                          ofproto.OFPCML_NO_BUFFER)]
        actions.extend(actions2)
        time.sleep(10)
        self.add_flow(datapath, 1000, match, ofproto.OFPP_ANY, ofproto.OFPG_ANY,actions)
        print("ipv6 add push_vlan flow ok!")    

        match = parser.OFPMatch(eth_type=0x0800)
        actions = []
        actions1 = [parser.OFPActionSetNwTtl(nw_ttl=32)]
        actions.extend(actions1)
        actions2 = [parser.OFPActionOutput(2,
                                          ofproto.OFPCML_NO_BUFFER)]
        actions.extend(actions2)
        time.sleep(10)
        self.add_flow(datapath, 1000, match, ofproto.OFPP_ANY, ofproto.OFPG_ANY,actions)
        print("set nw ttl flow ok!")    

        match = parser.OFPMatch(eth_type=0x0800)
        actions = []
        actions1 = [parser.OFPActionSetField(eth_type=0x8848)]
        actions.extend(actions1)
        actions2 = [parser.OFPActionOutput(2,
                                          ofproto.OFPCML_NO_BUFFER)]
        actions.extend(actions2)
        time.sleep(10)
        self.add_flow(datapath, 1000, match, ofproto.OFPP_ANY, ofproto.OFPG_ANY,actions)
        print("add push_vlan flow ok!")    

        match = parser.OFPMatch(eth_type=0x86dd)
        actions = []
        actions1 = [parser.OFPActionSetField(eth_type=0x8848)]
        actions.extend(actions1)
        actions2 = [parser.OFPActionOutput(2,
                                          ofproto.OFPCML_NO_BUFFER)]
        actions.extend(actions2)
        time.sleep(10)
        self.add_flow(datapath, 1000, match, ofproto.OFPP_ANY, ofproto.OFPG_ANY,actions)
        print("ipv6 add push_vlan flow ok!")    

        match = parser.OFPMatch(eth_type=0x0806)
        actions = []
        actions1 = [parser.OFPActionSetField(eth_type=0x8848)]
        actions.extend(actions1)
        actions2 = [parser.OFPActionOutput(2,
                                          ofproto.OFPCML_NO_BUFFER)]
        actions.extend(actions2)
        time.sleep(10)
        self.add_flow(datapath, 1000, match, ofproto.OFPP_ANY, ofproto.OFPG_ANY,actions)
        print("ipv6 add push_vlan flow ok!") 

        match = parser.OFPMatch(eth_type=0x86dd,ip_proto=6,ip_dscp=9)
        actions = []
        actions1 = [parser.OFPActionSetField(ip_dscp=19)]
        actions.extend(actions1)
        actions2 = [parser.OFPActionOutput(2,
                                          ofproto.OFPCML_NO_BUFFER)]
        actions.extend(actions2)
        time.sleep(10)
        self.add_flow(datapath, 1000, match, ofproto.OFPP_ANY, ofproto.OFPG_ANY,actions)
        print("add modify ip_dscp flow ok!")

        match = parser.OFPMatch(eth_type=0x86dd,ip_proto=6,ip_dscp=10)
        actions = []
        actions1 = [parser.OFPActionSetField(ip_dscp=20)]
        actions.extend(actions1)
        actions2 = [parser.OFPActionOutput(2,
                                          ofproto.OFPCML_NO_BUFFER)]
        actions.extend(actions2)
        time.sleep(10)
        self.add_flow(datapath, 1000, match, ofproto.OFPP_ANY, ofproto.OFPG_ANY,actions)
        print("add modify ip_dscp flow ok!")

    def add_flow(self, datapath, priority, match, outport, outgroup, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                out_port=outport, out_group=outgroup, match=match, instructions=inst)
        datapath.send_msg(mod)

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
