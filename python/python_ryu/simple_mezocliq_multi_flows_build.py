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
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

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
        
    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        datapath.send_msg(mod)

    def add_flow1(self, datapath, priority, match, actions, flags, command):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        mod = parser.OFPFlowMod(datapath=datapath, priority=32768,table_id=0,flags=1,match=match, instructions=inst, command=command)
        datapath.send_msg(mod)

    def del_flows(self, datapath, table_id,  match, command, flags):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = []
        mod = parser.OFPFlowMod(table_id=table_id,datapath=datapath, match=match, out_port=datapath.ofproto.OFPP_ANY, out_group = datapath.ofproto.OFPG_ANY,command=3, flags=1, instructions=inst)

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

        #dMacs=self.inceaseMac(num=100, mac='22:11:11:11:11:11')
        print 'dst:', dst
        if dst == '22:00:00:00:00:00':
            print 'dst:', dst

            actions = [parser.OFPActionOutput(2)]
            dMacs=self.inceaseMac(num=1000, mac='22:11:11:11:11:11')

            for dst in dMacs:
                match = parser.OFPMatch(eth_dst=dst, vlan_vid=1000, vlan_pcp=0)
                self.add_flow1(datapath, 32768, match, actions, flags=1, command=ofproto.OFPFC_ADD)
        elif dst == '22:00:00:00:00:01':
            match = parser.OFPMatch(vlan_vid=1000, vlan_pcp=0)
            self.del_flows(datapath, table_id=0, match=match, command=ofproto.OFPFC_DELETE, flags=1)
