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

from ryu.controller.handler import *
from ryu.topology import event
from ryu.controller import handler
from ryu.base import app_manager
from ryu.controller import mac_to_port
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_2
from ryu.lib.mac import haddr_to_str
from ryu.lib.packet import packet
from ryu.lib.packet import *
from ryu.lib import mac

UINT16_MAX = 0xffff
UINT32_MAX = 0xffffffff
UINT64_MAX = 0xffffffffffffffff


LOG = logging.getLogger('ryu.app.picaRegressionBasic')

# TODO: we should split the handler into two parts, protocol
# independent and dependant parts.

# TODO: can we use dpkt python library?

# TODO: we need to move the followings to something like db


class PicaRegressionBasic(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_2.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(PicaRegressionBasic, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

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

    def randomMAC(self):
        import random
        mac = [ 0x00, 0x16, 0x3e, random.randint(0x00, 0x7f), random.randint(0x00, 0xff), random.randint(0x00, 0xff) ]
        return ':'.join(map(lambda x: "%02x" % x, mac))

    def mask_ntob(self, mask, err_msg=None):
        try:
            return (UINT32_MAX << (32 - mask)) & UINT32_MAX
        except ValueError:
            msg = 'illegal netmask'
            if err_msg is not None:
                msg = '%s %s' % (err_msg, msg)
            raise ValueError(msg)

    def match_v12(self, datapath, in_port=None, dl_dst=None, dl_src=None, dl_type=None, vlan_vid=None, vlan_pcp=None, ip_dscp=None, ip_ecn=None, ip_proto=None, ipv4_src=None, ipv4_dst=None, ipv4_dst_mask=None, tcp_src=None, tcp_dst=None, udp_src=None, udp_dst=None):
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
            
        if ipv4_dst is not None:
            ipv4_dst = self.ipv4_to_int(ipv4_dst)
            match.set_ipv4_dst(ipv4_dst)
            
        if ipv4_dst_mask is not None:
            #ipv4_dst = self.ipv4_to_int(ipv4_dst)
            match.set_ipv4_dst_masked(ipv4_dst, self.mask_ntob(ipv4_dst_mask))

        if tcp_src is not None:
            match.set_tcp_src(tcp_src)
            
        if tcp_dst is not None:
            match.set_tcp_dst(tcp_dst)
            
        if udp_src is not None:
            match.set_udp_src(udp_src)
            
        if udp_dst is not None:
            match.set_udp_dst(udp_dst)

        return match

    def action_v12(self, datapath, actions=None, dl_dst=None, dl_src=None, dl_type=None, vlan_vid=None, vlan_pcp=None, ip_dscp=None, ip_ecn=None, ip_proto=None, ipv4_src=None, ipv4_dst=None, tcp_src=None, tcp_dst=None, udp_src=None, udp_dst=None, out_port=None):

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

    def bucket_v12(self, datapath, actions = [], len_=0, weight=0, watch_port=0, watch_group=0):
        buckets = [datapath.ofproto_parser.OFPBucket(len_=len_, weight=weight, watch_port=watch_port,watch_group=watch_group, actions=actions)]
        return buckets

    def group_v12(self, datapath, group_id=0, type_=0, command=0, buckets=None):
        
        group = datapath.ofproto_parser.OFPGroupMod(datapath=datapath,command=command,type_=type_,group_id=group_id,buckets=buckets)
        datapath.send_msg(group)

    def ipv4_to_int(self, string):
        ip = string.split('.')
        assert len(ip) == 4
        i = 0
        for b in ip:
            b = int(b)
            i = (i << 8) | b
        return i
    
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
        for p in pkt.protocols:
            if hasattr(p, 'protocol_name'):
                if p.protocol_name == name:
                    return p

    def dir_print(self, msg):
        print "%s\n" % dir(msg)

    def packet_print(self,pkt):
        # Mac information
        mac_addr = self.find_protocol(pkt,'ethernet')       
        if mac_addr:
            mac_src = haddr_to_str(mac_addr.src)
            mac_dst = haddr_to_str(mac_addr.dst)
            mac_ethertype = mac_addr.ethertype
            LOG.info("########Mac information########")
            LOG.info("mac_src:%s mac_dst:%s mac_ethertype:%s\n",mac_src,mac_dst,mac_ethertype)

        # Vlan information
        vlan = self.find_protocol(pkt, 'vlan')
        if vlan:
            vlan_pcp = vlan.pcp
            vlan_cfi = vlan.cfi
            vlan_vid = vlan.vid
            vlan_ethertype = vlan.ethertype
            LOG.info("########Vlan information########")
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
            ip_proto = ipv4.proto
            ip_csum = ipv4.csum
            ip_src = socket.inet_ntoa(struct.pack('I',socket.htonl(ipv4.src)))
            ip_dst = socket.inet_ntoa(struct.pack('I',socket.htonl(ipv4.dst)))
            #ip_length = ipv4.length
            ip_option = ipv4.option
            LOG.info("########IPv4 information########")
            LOG.info("ip_version:%s ip_header_length:%s tos:%s ip_total_length:%s",ip_version,ip_header_length,ip_tos,ip_total_length)
            LOG.info("ip_identification:%s ip_flags:%s ip_offset:%s ip_ttl:%s",ip_identification,ip_flags,ip_offset,ip_ttl)
            LOG.info("ip_proto:%s ip_csum:%s ip_src:%s ip_dst:%s",ip_proto,ip_csum,ip_src,ip_dst)
            LOG.info("ip_option:%s\n",ip_option)

        # Arp information
        arp = self.find_protocol(pkt, 'arp')
        if arp:
            arp_hwtype = arp.hwtype
            arp_proto = arp.proto
            arp_hlen = arp.hlen
            arp_plen = arp.plen
            arp_opcode = arp.opcode
            arp_src_mac = haddr_to_str(arp.src_mac)
            arp_src_ip = socket.inet_ntoa(struct.pack('I',socket.htonl(arp.src_ip)))
            arp_dst_mac = haddr_to_str(arp.dst_mac)
            arp_dst_ip = socket.inet_ntoa(struct.pack('I',socket.htonl(arp.src_ip)))
            #arp_length = arp.length
            LOG.info("########Arp information########")
            LOG.info("arp_hwtype:%s arp_proto:%s arp_hlen:%s arp_plen:%s",arp_hwtype,arp_proto,arp_hlen,arp_plen)
            LOG.info("arp_opcode:%s arp_src_mac:%s arp_src_ip:%s arp_dst_mac:%s",arp_opcode,arp_src_mac,arp_src_ip,arp_dst_mac)
            LOG.info("arp_dst_ip:%s\n",arp_dst_ip)

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
            LOG.info("########Tcp information########")
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
            LOG.info("########Udp information########")
            LOG.info("udp_src_port:%s udp_dst_port:%s udp_total_length:%s",udp_src_port,udp_dst_port,udp_total_length)
            LOG.info("udp_csum:%s\n",udp_csum)

        # icmp information
        icmp = self.find_protocol(pkt, 'icmp')
        if icmp:
            icmp_type = icmp.type
            icmp_code = icmp.code
            icmp_csum = icmp.csum
            icmp_data = icmp.data
            LOG.info("########Icmp information########")
            LOG.info("icmp_type:%s icmp_code:%s icmp_csum:%s icmp_data:%s\n",icmp_type,icmp_code,icmp_csum,icmp_data)
            
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

        LOG.info("\n########in_port information########")
        LOG.info("in_port:%s\n", in_port)

        # packet information (primary packets: LOG.info("packets:%s", pkt.protocols))
        pkt = packet.Packet(array.array('B', ev.msg.data))
        self.packet_print(pkt)

        # get the src, dst mac address
        mac_addr = self.find_protocol(pkt,'ethernet')
        if mac_addr:
            src = haddr_to_str(mac_addr.src)
            dst = haddr_to_str(mac_addr.dst)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        # output port information
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        LOG.info("########out_port information########")
        LOG.info("out_port:%s\n",out_port)

        # match information
        in_port = 1
        dl_dst = '22:00:00:00:00:00'
        dl_src = '22:11:11:11:11:11'
        dl_type=0x0800
        vlan_vid=2000
        vlan_pcp=7
        ip_dscp=0
        ip_ecn=0
        ip_proto=6
        tcp_src=1
        tcp_dst=1
        ipv4_src = '192.168.100.100'
        ipv4_dst = '192.168.100.200'
        match = self.match_v12(datapath,in_port=in_port, dl_dst=dl_dst, dl_src=dl_src,\
                                            dl_type=dl_type,vlan_vid=vlan_vid,vlan_pcp=vlan_pcp,\
                                            ip_dscp=ip_dscp,ip_ecn=ip_ecn,ip_proto=ip_proto,\
                                            ipv4_src=ipv4_src, ipv4_dst=ipv4_dst,tcp_src=tcp_src,tcp_dst=tcp_dst)
        LOG.info("########match information########")
        print "match:%s\n" % match

        # action information
        out_dl_dst = '22:11:11:11:11:11'
        out_dl_src = '22:00:00:00:00:00'
        out_ip_dscp = 8
        actions = self.action_v12(datapath,out_port=2, dl_dst=out_dl_dst,dl_src=out_dl_src,vlan_vid=4094,vlan_pcp=3,ip_dscp=out_ip_dscp)

        LOG.info("########action information########")
        print "actions:%s\n" % actions

        # add or delete flow
        if src == '22:11:11:11:11:11':
            LOG.info("#######add flow########")
            self.flow_v12(datapath, table_id=0, match=match, flags=1, command=0, buffer_id=0xffffffff, actions=actions)
        elif src == '22:11:11:11:11:12':
            LOG.info("#######add 1000 random flow########")
            for i in range(1000):
                dl_src = self.randomMAC()
                match = self.match_v12(datapath,in_port=in_port, dl_dst=dl_dst, dl_src=dl_src,\
                                        dl_type=dl_type,vlan_vid=vlan_vid,vlan_pcp=vlan_pcp,\
                                        ip_dscp=ip_dscp,ip_ecn=ip_ecn,ip_proto=ip_proto,\
                                        ipv4_src=ipv4_src, ipv4_dst=ipv4_dst,tcp_src=tcp_src,tcp_dst=tcp_dst)
                self.flow_v12(datapath, table_id=0, match=match, flags=1, command=0, buffer_id=0xffffffff, actions=actions)
        elif src == '22:22:22:22:22:22':
            LOG.info("#######add 1000 mac increase flow########")
            sMacs=self.inceaseMac(num=1000, mac='22:22:22:22:22:22')
            print('sMacs is ', sMacs)
            for sMac in sMacs:
		print('sMac is ', sMac)
                match = self.match_v12(datapath,in_port=in_port, dl_dst=dl_dst, dl_src=sMac,\
                                    dl_type=dl_type,vlan_vid=vlan_vid,vlan_pcp=vlan_pcp,\
                                    ip_dscp=ip_dscp,ip_ecn=ip_ecn,ip_proto=ip_proto,\
                                    ipv4_src=ipv4_src, ipv4_dst=ipv4_dst,tcp_src=tcp_src,tcp_dst=tcp_dst)
                self.flow_v12(datapath, table_id=0, match=match, flags=1, command=0, buffer_id=0xffffffff, actions=actions)
        elif src == '22:11:11:11:11:14':
            LOG.info("#######delete flow########")
            match_del = self.match_v12(datapath,in_port=1, dl_dst=dl_dst, dl_src=dl_src)
            self.flow_v12(datapath, table_id=0, flags=1, match=match_del, command=3)

        # add or delete group
        if src == '22:11:11:11:11:15':
            LOG.info("#######add group########")
            match_group = self.match_v12(datapath,in_port=in_port, dl_dst=dl_dst, dl_src=dl_src,\
                                       dl_type=dl_type,vlan_vid=vlan_vid,vlan_pcp=vlan_pcp,\
                                       ip_dscp=ip_dscp,ip_ecn=ip_ecn,ip_proto=ip_proto,\
                                       ipv4_src=ipv4_src, ipv4_dst=ipv4_dst,tcp_src=tcp_src,tcp_dst=tcp_dst)

            bucket_output = [datapath.ofproto_parser.OFPActionOutput(2, 0)]
            bucket = self.bucket_v12(datapath, actions=bucket_output)
            self.group_v12(datapath, group_id=2238, command=0, buckets=bucket)
            actions = [datapath.ofproto_parser.OFPActionGroup(2238)]
            self.flow_v12(datapath, table_id=0, match=match_group, buffer_id=0xffffffff,command=0, actions=actions)
        elif src == '22:11:11:11:11:16':
            match_group = self.match_v12(datapath,in_port=in_port, dl_dst=dl_dst)
            self.flow_v12(datapath, table_id=0, command=3)
            #bucket_output = [datapath.ofproto_parser.OFPActionOutput(2, 0)]
            bucket_output = []
            bucket = self.bucket_v12(datapath, actions=bucket_output)
            self.group_v12(datapath, type_=0,group_id=2239, command=datapath.ofproto.OFPGC_DELETE,buckets=bucket)
        elif src == '22:11:11:11:11:17':
            LOG.info("#######add group to output group########")
            match_group = self.match_v12(datapath,in_port=in_port, dl_dst=dl_dst, dl_src=dl_src,\
                                       dl_type=dl_type,vlan_vid=vlan_vid,vlan_pcp=vlan_pcp,\
                                       ip_dscp=ip_dscp,ip_ecn=ip_ecn,ip_proto=ip_proto,\
                                       ipv4_src=ipv4_src, ipv4_dst=ipv4_dst,tcp_src=tcp_src,tcp_dst=tcp_dst)

            bucket_output = [datapath.ofproto_parser.OFPActionOutput(2, 0)]
            bucket = self.bucket_v12(datapath, actions=bucket_output)
            self.group_v12(datapath, group_id=2239, command=0, buckets=bucket)
            actions = [datapath.ofproto_parser.OFPActionGroup(2239)]
            self.flow_v12(datapath, table_id=0, match=match_group, command=0, actions=actions)            

            bucket_output = [datapath.ofproto_parser.OFPActionGroup(2239)]
            bucket = self.bucket_v12(datapath, actions=bucket_output)
            self.group_v12(datapath, group_id=2240, command=0, buckets=bucket)
        elif src == '22:11:11:11:11:18':
            LOG.info("#######add ecmp flow########")
            dl_dst = '22:00:00:00:00:12'
            dl_type=0x0800
            vlan_vid=1
            ip_proto=6
            ipv4_dst = '10.10.50.99'
            match = self.match_v12(datapath,dl_dst=dl_dst, dl_type=dl_type,vlan_vid=vlan_vid,ipv4_dst=ipv4_dst)
            
            actions = []
            out_dl_dst = '12:34:56:78:9C:16'
            out_vlan = 2000
            out_port = 2
            actions1 = self.action_v12(datapath, out_port=out_port, dl_dst=out_dl_dst,vlan_vid=out_vlan)
            out_dl_dst = '12:34:56:78:9C:22'
            out_vlan = 4094
            out_port = 3
            actions = self.action_v12(datapath, actions = actions1, out_port=out_port, dl_dst=out_dl_dst,vlan_vid=out_vlan)
            self.flow_v12(datapath, table_id=0, match=match, flags=1, command=0, buffer_id=0xffffffff, actions=actions)
        elif src == '22:11:11:11:11:19':
            LOG.info("#######add flow including mask########")
            dl_dst = '01:00:5e:00:00:0d'
            dl_src = '80:71:1f:a8:f6:00'
            dl_type=0x0800
            ip_proto=103
            ipv4_dst = '224.0.0.13'
            ipv4_src = '163.7.136.2'
            ipv4_dst_mask = 23
            match = self.match_v12(datapath,in_port=12, ip_proto=ip_proto,dl_dst=dl_dst, dl_type=dl_type,vlan_vid=vlan_vid,ipv4_dst=ipv4_dst,ipv4_dst_mask=ipv4_dst_mask)

            actions = []
            out_dl_dst = '12:a1:a1:a1:a3:02'
            out_port = 13
            actions = self.action_v12(datapath, out_port=out_port, dl_dst=out_dl_dst)
            self.flow_v12(datapath, table_id=0, match=match, flags=1, command=0, buffer_id=0xffffffff, actions=actions)

    @set_ev_cls(ofp_event.EventOFPFlowRemoved, MAIN_DISPATCHER)
    def _flow_removed_handler(self, ev):
        LOG.info("###########delete flow event")
        msg = ev.msg
        print "dir(msg):"
        self.dir_print(msg)

        print "dir(msg.match):"
        self.dir_print(msg.match)

        for f in msg.match.fields:
            print "f:%s\n" % f
            if f.header == ofproto_v1_2.OXM_OF_IN_PORT:
                in_port = f.value

        print "del in_port:%s\n" % in_port

    #@set_ev_handler(ofp_event.EventOFPHello, HANDSHAKE_DISPATCHER)
    def hello_handler(self, ev):
		print '9999999999999999999999'

    #@set_ev_handler(ofp_event.EventOFPSwitchFeatures, MAIN_DISPATCHER)
    #@set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
		print '##############Connected to Pica8 switch############'
		time.sleep(15)
		print '##############Finished install flows############'
		

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def _port_status_handler(self, ev):
        msg = ev.msg
        self.dir_print(msg)
        self.dir_print(msg.desc)
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
