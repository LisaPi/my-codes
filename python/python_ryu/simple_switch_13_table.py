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
from ryu.lib import mac

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
        self.add_flow(datapath, 0, 0, match, actions)

    def add_flow(self, datapath, table_id, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        mod = parser.OFPFlowMod(table_id=table_id,datapath=datapath, priority=priority,out_port=0,out_group=0,match=match, instructions=inst)

        datapath.send_msg(mod)

    def ipv4_to_int(self, string):
        ip = string.split('.')
        assert len(ip) == 4
        i = 0
        for b in ip:
            b = int(b)
            i = (i << 8) | b
        return i

    def set_match(self, datapath, in_port=None, dl_dst=None, dl_dst_mask=None, dl_src=None, dl_src_mask=None, dl_type=None, vlan_vid=None, vlan_pcp=None, ip_dscp=None, ip_ecn=None, ip_proto=None, ipv4_src=None, ipv4_src_mask=None, ipv4_dst=None, ipv4_dst_mask=None, tcp_src=None, tcp_dst=None, udp_src=None, udp_dst=None):
        match = datapath.ofproto_parser.OFPMatch()
        if in_port is not None:
            match.set_in_port(in_port)
            
        if dl_dst is not None:
            dl_dst = mac.haddr_to_bin(dl_dst)
            match.set_dl_dst(dl_dst)
            if dl_dst_mask is not None:
                match.set_dl_dst_masked(dl_dst, mac.haddr_to_bin(dl_dst_mask))
            
        if dl_src is not None:
            dl_src = mac.haddr_to_bin(dl_src)
            match.set_dl_src(dl_src)
            if dl_src_mask is not None:
                match.set_dl_src_masked(dl_src, mac.haddr_to_bin(dl_src_mask))
            
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
                match.set_ipv4_src_masked(ipv4_src, self.ipv4_to_int(ipv4_src_mask))
            
        if ipv4_dst is not None:
            ipv4_dst = self.ipv4_to_int(ipv4_dst)
            match.set_ipv4_dst(ipv4_dst)
            if ipv4_dst_mask is not None:
                match.set_ipv4_dst_masked(ipv4_dst, self.ipv4_to_int(ipv4_dst_mask))
            
        if tcp_src is not None:
            match.set_tcp_src(tcp_src)
            
        if tcp_dst is not None:
            match.set_tcp_dst(tcp_dst)
            
        if udp_src is not None:
            match.set_udp_src(udp_src)
            
        if udp_dst is not None:
            match.set_udp_dst(udp_dst)

        return match

    def set_action(self, datapath, actions=None, dl_dst=None, dl_src=None, dl_type=None, vlan_vid=None, vlan_pcp=None, ip_dscp=None, ip_ecn=None, ip_proto=None, ipv4_src=None, ipv4_dst=None, tcp_src=None, tcp_dst=None, udp_src=None, udp_dst=None, out_port=None):

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
            actions.append(datapath.ofproto_parser.OFPActionOutput(out_port, 0))
        else:
            actions.append(datapath.ofproto_parser.OFPActionOutput(ofproto.OFPP_ALL, 0))
       
        return actions

    def send_table_flow(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.
        match = self.set_match(datapath, dl_type=0x0800,vlan_vid=10)
        actions = self.set_action(datapath, dl_dst='00:a1:cd:53:c6:55', vlan_vid=0,out_port=14)
        self.add_flow(datapath, 0, 0, match, actions)

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
            self.add_flow(datapath, 0, 1, match, actions)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        print 'dst', dst
        if dst == '22:00:00:00:00:00':
            self.send_table_flow(datapath)  

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
