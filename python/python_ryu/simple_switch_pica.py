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

from ryu import utils
from ryu.controller import handler
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, HANDSHAKE_DISPATCHER
from ryu.base import app_manager
from ryu.controller import mac_to_port
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.mac import haddr_to_str
from ryu.lib.packet import packet
from ryu.lib.packet import *
from ryu.lib import mac
from ryu.ofproto import ether

LOG = logging.getLogger('ryu.app.simple_switch_pica')

# TODO: we should split the handler into two parts, protocol
# independent and dependant parts.

# TODO: can we use dpkt python library?

# TODO: we need to move the followings to something like db


class SimpleSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

    # feature request handler
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
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, 0, match, actions)

    # feature request sender
    def send_features_request(self, datapath):
        ofp_parser = datapath.ofproto_parser

        req = ofp_parser.OFPFeaturesRequest(datapath)
        datapath.send_msg(req)

    # desc stats request sender
    def send_desc_stats_request(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        req = ofp_parser.OFPDescStatsRequest(datapath, 0)
        datapath.send_msg(req)

    # desc stats request handler
    @set_ev_cls(ofp_event.EventOFPDescStatsReply, MAIN_DISPATCHER)
    def desc_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.debug('DescStats: mfr_desc=%s hw_desc=%s sw_desc=%s '
                          'serial_num=%s dp_desc=%s',
                          body.mfr_desc, body.hw_desc, body.sw_desc,
                          body.serial_num, body.dp_desc)

    # table stats request sender
    def send_table_stats_request(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        req = ofp_parser.OFPTableStatsRequest(datapath, 0)
        datapath.send_msg(req)

    # table stats request handler
    @set_ev_cls(ofp_event.EventOFPTableStatsReply, MAIN_DISPATCHER)
    def table_stats_reply_handler(self, ev):
        tables = []
        for stat in ev.msg.body:
            tables.append('table_id=%d active_count=%d lookup_count=%d '
                          ' matched_count=%d' %
                           (stat.table_id, stat.active_count,
                           stat.lookup_count, stat.matched_count))
         self.logger.debug('TableStats: %s', tables)

    # port mod sender
    def send_port_mod(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        port_no = 1
        hw_addr = '21:c8:e8:76:1e:7f'
        config = 0
        mask = (ofp.OFPPC_PORT_DOWN | ofp.OFPPC_NO_RECV |
                ofp.OFPPC_NO_FWD | ofp.OFPPC_NO_PACKET_IN)
        advertise = (ofp.OFPPF_10MB_HD | ofp.OFPPF_100MB_FD |
                     ofp.OFPPF_1GB_FD | ofp.OFPPF_COPPER |
                     ofp.OFPPF_AUTONEG | ofp.OFPPF_PAUSE |
                     ofp.OFPPF_PAUSE_ASYM)
        req = ofp_parser.OFPPortMod(datapath, port_no, hw_addr, config, mask, advertise)
        datapath.send_msg(req)

    # table mod sender
    def send_table_mod(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        req = ofp_parser.OFPTableMod(datapath, 1, 3)
        datapath.send_msg(req)

    # port stats request sender
    def send_port_stats_request(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        req = ofp_parser.OFPPortStatsRequest(datapath, 0, ofp.OFPP_ANY)
        datapath.send_msg(req)

    # port stats requst handler
    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def port_stats_reply_handler(self, ev):
        ports = []
        for stat in ev.msg.body:
            ports.append('port_no=%d '
                         'rx_packets=%d tx_packets=%d '
                         'rx_bytes=%d tx_bytes=%d '
                         'rx_dropped=%d tx_dropped=%d '
                         'rx_errors=%d tx_errors=%d '
                         'rx_frame_err=%d rx_over_err=%d rx_crc_err=%d '
                         'collisions=%d duration_sec=%d duration_nsec=%d' %
                         (stat.port_no,
                          stat.rx_packets, stat.tx_packets,
                          stat.rx_bytes, stat.tx_bytes,
                          stat.rx_dropped, stat.tx_dropped,
                          stat.rx_errors, stat.tx_errors,
                          stat.rx_frame_err, stat.rx_over_err,
                          stat.rx_crc_err, stat.collisions,
                          stat.duration_sec, stat.duration_nsec))
        self.logger.debug('PortStats: %s', ports)

    # flow stats reply handler
    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def flow_stats_reply_handler(self, ev):
        flows = []
        for stat in ev.msg.body:
            flows.append('table_id=%s '
                         'duration_sec=%d duration_nsec=%d '
                         'priority=%d '
                         'idle_timeout=%d hard_timeout=%d flags=0x%04x '
                         'cookie=%d packet_count=%d byte_count=%d '
                         'match=%s instructions=%s' %
                         (stat.table_id,
                          stat.duration_sec, stat.duration_nsec,
                          stat.priority,
                          stat.idle_timeout, stat.hard_timeout, stat.flags,
                          stat.cookie, stat.packet_count, stat.byte_count,
                          stat.match, stat.instructions))
        self.logger.info('FlowStats: %s', flows)

    # flow stats request sender
    def send_flow_stats_request(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        cookie = cookie_mask = 0 
        match = parser.OFPMatch()
        req = parser.OFPFlowStatsRequest(datapath, 0,
                                         ofproto.OFPTT_ALL,
                                         ofproto.OFPP_ANY, ofproto.OFPG_ANY,
                                         cookie, cookie_mask,
                                         match)
        datapath.send_msg(req)

    # aggregate stats request sender
    def send_aggregate_stats_request(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        cookie = cookie_mask = 0
        match = ofp_parser.OFPMatch(in_port=1)
        req = ofp_parser.OFPAggregateStatsRequest(datapath, 0,
                                                  ofp.OFPTT_ALL,
                                                  ofp.OFPP_ANY,
                                                  ofp.OFPG_ANY,
                                                  cookie, cookie_mask,
                                                  match)
        datapath.send_msg(req)

    # aggregate stats request handler
    @set_ev_cls(ofp_event.EventOFPAggregateStatsReply, MAIN_DISPATCHER)
    def aggregate_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.debug('AggregateStats: packet_count=%d byte_count=%d '
                          'flow_count=%d',
                          body.packet_count, body.byte_count,
                          body.flow_count)

    # queue stats request sender
    def send_queue_stats_request(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        req = ofp_parser.OFPQueueStatsRequest(datapath, 0, ofp.OFPP_ANY,
                                              ofp.OFPQ_ALL)
        datapath.send_msg(req)

    # queue stats request handler
    @set_ev_cls(ofp_event.EventOFPQueueStatsReply, MAIN_DISPATCHER)
    def queue_stats_reply_handler(self, ev):
        queues = []
        for stat in ev.msg.body:
            queues.append('port_no=%d queue_id=%d '
                          'tx_bytes=%d tx_packets=%d tx_errors=%d '
                          'duration_sec=%d duration_nsec=%d' %
                          (stat.port_no, stat.queue_id,
                           stat.tx_bytes, stat.tx_packets, stat.tx_errors,
                           stat.duration_sec, stat.duration_nsec))
        self.logger.debug('QueueStats: %s', queues)

    # group features stats request
    def send_group_features_stats_request(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        req = ofp_parser.OFPGroupFeaturesStatsRequest(datapath, 0)
        datapath.send_msg(req)

    # group features stats handler
    @set_ev_cls(ofp_event.EventOFPGroupFeaturesStatsReply, MAIN_DISPATCHER)
    def group_features_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.debug('GroupFeaturesStats: types=%d '
                          'capabilities=0x%08x max_groups=%s '
                          'actions=%s',
                          body.types, body.capabilities,
                          body.max_groups, body.actions)

    # group stats request sender
    def send_group_stats_request(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        req = ofp_parser.OFPGroupStatsRequest(datapath, 0, ofp.OFPG_ALL)
        datapath.send_msg(req)

    # group stats request handler
    @set_ev_cls(ofp_event.EventOFPGroupStatsReply, MAIN_DISPATCHER)
    def group_stats_reply_handler(self, ev):
        groups = []
        for stat in ev.msg.body:
            groups.append('length=%d group_id=%d '
                          'ref_count=%d packet_count=%d byte_count=%d '
                          'duration_sec=%d duration_nsec=%d' %
                          (stat.length, stat.group_id,
                           stat.ref_count, stat.packet_count,
                           stat.byte_count, stat.duration_sec,
                           stat.duration_nsec))
        self.logger.debug('GroupStats: %s', groups)

    # meter stats request
    def send_meter_stats_request(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        req = ofp_parser.OFPMeterStatsRequest(datapath, 0, ofp.OFPM_ALL)
        datapath.send_msg(req)

    # meter stats request handler
    @set_ev_cls(ofp_event.EventOFPMeterStatsReply, MAIN_DISPATCHER)
    def meter_stats_reply_handler(self, ev):
        meters = []
        for stat in ev.msg.body:
            meters.append('meter_id=0x%08x len=%d flow_count=%d '
                          'packet_in_count=%d byte_in_count=%d '
                          'duration_sec=%d duration_nsec=%d '
                          'band_stats=%s' %
                          (stat.meter_id, stat.len, stat.flow_count,
                           stat.packet_in_count, stat.byte_in_count,
                           stat.duration_sec, stat.duration_nsec,
                           stat.band_stats))
        self.logger.debug('MeterStats: %s', meters)

    # meter features stats request
    def send_meter_features_stats_request(self, datapath):
        ofp_parser = datapath.ofproto_parser

        req = ofp_parser.OFPMeterFeaturesStatsRequest(datapath, 0)
        datapath.send_msg(req)

    # meter features stats handler
    @set_ev_cls(ofp_event.EventOFPMeterFeaturesStatsReply, MAIN_DISPATCHER)
    def meter_features_stats_reply_handler(self, ev):
        features = []
        for stat in ev.msg.body:
            features.append('max_meter=%d band_types=0x%08x '
                            'capabilities=0x%08x max_band=%d '
                            'max_color=%d' %
                            (stat.max_meter, stat.band_types,
                             stat.capabilities, stat.max_band,
                             stat.max_color))
        self.logger.debug('MeterFeaturesStats: %s', configs)

    # flow remove handler
    @set_ev_cls(ofp_event.EventOFPFlowRemoved, MAIN_DISPATCHER)
    def _flow_removed_handler(self, ev):
        LOG.info("###########delete flow event")
        msg = ev.msg
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto

        if msg.reason == ofproto.OFPRR_IDLE_TIMEOUT:
            reason = 'IDLE TIMEOUT'
        elif msg.reason == ofproto.OFPRR_HARD_TIMEOUT:
            reason = 'HARD TIMEOUT'
        elif msg.reason == ofproto.OFPRR_DELETE:
            reason = 'DELETE'
        elif msg.reason == ofproto.OFPRR_GROUP_DELETE:
            reason = 'GROUP DELETE'
        else:
            reason = 'unknown'

        self.logger.debug('OFPFlowRemoved received: '
                          'cookie=%d priority=%d reason=%s table_id=%d '
                          'duration_sec=%d duration_nsec=%d '
                          'idle_timeout=%d hard_timeout=%d '
                          'packet_count=%d byte_count=%d match.fields=%s',
                          msg.cookie, msg.priority, reason, msg.table_id,
                          msg.duration_sec, msg.duration_nsec,
                          msg.idle_timeout, msg.hard_timeout,
                          msg.packet_count, msg.byte_count, msg.match)

        for f in msg.match.fields:
            print "f:%s\n" % f
            if f.header == ofproto_v1_3.OXM_OF_IN_PORT:
                in_port = f.value
                print "del in_port:%s\n" % in_port

    # port status handler
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

    # echo request handler
    @set_ev_cls(ofp_event.EventOFPEchoRequest, [HANDSHAKE_DISPATCHER, CONFIG_DISPATCHER, MAIN_DISPATCHER])
    def echo_request_handler(self, ev):
        self.logger.debug('OFPEchoRequest received: data=%s', utils.hex_array(ev.msg.data))

    # echo request sender
    def send_echo_request(self, datapath, data):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        req = ofp_parser.OFPEchoRequest(datapath, data)
        datapath.send_msg(req)

    # echo reply handler
    @set_ev_cls(ofp_event.EventOFPEchoReply, [HANDSHAKE_DISPATCHER, CONFIG_DISPATCHER, MAIN_DISPATCHER])
    def echo_reply_handler(self, ev):
        self.logger.debug('OFPEchoReply received: data=%s', utils.hex_array(ev.msg.data))

    # echo reply sender
    def send_echo_reply(self, datapath, data):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        reply = ofp_parser.OFPEchoReply(datapath, data)
        datapath.send_msg(reply)

    # get config request sender
    def send_get_config_request(self, datapath):
        ofp_parser = datapath.ofproto_parser

        req = ofp_parser.OFPGetConfigRequest(datapath)
        datapath.send_msg(req)

    # get config reply handler
    @set_ev_cls(ofp_event.EventOFPGetConfigReply, MAIN_DISPATCHER)
    def get_config_reply_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        flags = []

        if msg.flags & ofp.OFPC_FRAG_NORMAL:
            flags.append('NORMAL')
        if msg.flags & ofp.OFPC_FRAG_DROP:
            flags.append('DROP')
        if msg.flags & ofp.OFPC_FRAG_REASM:
            flags.append('REASM')
        self.logger.debug('OFPGetConfigReply received: '
                             'flags=%s miss_send_len=%d',
                              ','.join(flags), msg.miss_send_len)

    # set config sender
    def send_set_config(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        req = ofp_parser.OFPSetConfig(datapath, ofp.OFPC_FRAG_NORMAL, 256)
        datapath.send_msg(req)

    # packet out sender
    def send_packet_out(self, datapath, buffer_id, in_port):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        actions = [ofp_parser.OFPActionOutput(ofp.OFPP_FLOOD, 0)]
        req = ofp_parser.OFPPacketOut(datapath, buffer_id,
                                          in_port, actions)
        datapath.send_msg(req)

    # ipv4 to int function
    def ipv4_to_int(self, string):
        ip = string.split('.')
        assert len(ip) == 4
        i = 0
        for b in ip:
            b = int(b)
            i = (i << 8) | b
        return i

    # Generate any number mac address in incr order
    def gene_incr_mac(self, num=None, mac=None):
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

    # Generate random mac
    def gene_random_mac(self):
        import random
        mac = [ 0x00, 0x16, 0x3e, random.randint(0x00, 0x7f), random.randint(0x00, 0xff), random.randint(0x00, 0xff) ]
        return ':'.join(map(lambda x: "%02x" % x, mac))

    # Add flow
    def add_flow(self, datapath, table_id, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(table_id=table_id,datapath=datapath, priority=priority,out_port=0,out_group=0,match=match, flags=1, instructions=inst)

        datapath.send_msg(mod)

    # Set flow match
    def set_flow_match(self, datapath, in_port=None, dl_dst=None, dl_src=None, dl_type=None, vlan_vid=None, vlan_pcp=None, ip_dscp=None, ip_ecn=None, ip_proto=None, ipv4_src=None, ipv4_dst=None, tcp_src=None, tcp_dst=None, udp_src=None, udp_dst=None, pbb_isid=None):
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
            
        if tcp_src is not None:
            match.set_tcp_src(tcp_src)
            
        if tcp_dst is not None:
            match.set_tcp_dst(tcp_dst)
            
        if udp_src is not None:
            match.set_udp_src(udp_src)
            
        if udp_dst is not None:
            match.set_udp_dst(udp_dst)

        if pbb_isid is not None:
            match.set_pbb_isid(pbb_isid)

        return match

    # Set flow action
    def set_flow_action(self, datapath, dl_dst=None, dl_src=None, dl_type=None, vlan_vid=None, vlan_pcp=None, ip_dscp=None, ip_ecn=None, ip_proto=None, ipv4_src=None, ipv4_dst=None, tcp_src=None, tcp_dst=None, udp_src=None, udp_dst=None, out_port=None):

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

    # Set bucket
    def set_bucket(self, datapath, actions = [], len_=0, weight=0, watch_port=0xffffffff, watch_group=0xffffffff):
        buckets = [datapath.ofproto_parser.OFPBucket(len_=len_, weight=weight, watch_port=watch_port,watch_group=watch_group, actions=actions)]
        return buckets

    # Set group
    def set_group(self, datapath, group_id=0, type_=0, command=0, buckets=None):
        
        group = datapath.ofproto_parser.OFPGroupMod(datapath=datapath,command=command,type_=type_,group_id=group_id,buckets=buckets)
        datapath.send_msg(group)

    # Set meter
    def set_meter(self, datapath, command=0, flags=0, meter_id=0, bands=[]):
        meter = datapath.ofproto_parser.OFPMeterMod(datapath=datapath,command=command,flags=flags, meter_id=meter_id, bands=bands)
        datapath.send_msg(meter)

    # Set flow
    def set_flow(self, datapath, cookie=0, cookie_mask=0, table_id=0, command=None, idle_timeout=0, hard_timeout=0, \
                 priority=0, buffer_id=None, match=None, actions=None, inst_type=None, out_port=None, out_group=None, flags=0, inst=None):
        if command is None:
            command = datapath.ofproto.OFPFC_ADD

        if buffer_id is None:
            buffer_id = datapath.ofproto.OFPCML_NO_BUFFER
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
 
    # Push vlan flow
    def push_vlan_flow(self, datapath, priority, match, vlan_vid, out_port):

        actions = []

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        field = datapath.ofproto.OXM_OF_VLAN_VID
        f = datapath.ofproto_parser.OFPMatchField.make(field, vlan_vid)

        eth_VLAN = ether.ETH_TYPE_8021Q
        actions.append(datapath.ofproto_parser.OFPActionPushVlan(eth_VLAN)) 
        actions.append(datapath.ofproto_parser.OFPActionSetField(f))
        actions.append(datapath.ofproto_parser.OFPActionOutput(out_port, 0))

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(table_id=0,datapath=datapath, priority=priority,out_port=0,out_group=0,match=match, flags=1, instructions=inst)

        datapath.send_msg(mod)

    # Pop vlan flow
    def pop_vlan_flow(self, datapath, priority, match, out_port):

        actions = []

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        actions.append(datapath.ofproto_parser.OFPActionPopVlan())
        actions.append(datapath.ofproto_parser.OFPActionOutput(out_port, 0))

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(table_id=0,datapath=datapath, priority=priority,out_port=0,out_group=0,match=match, flags=1, instructions=inst)

        datapath.send_msg(mod)

    # Push mpls flow
    def push_mpls_flow(self, datapath, priority, match, mpls_label, mpls_tc, mpls_ttl, out_port):

        actions = []

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        eth_MPLS = ether.ETH_TYPE_MPLS
        f_label = datapath.ofproto_parser.OFPMatchField.make(datapath.ofproto.OXM_OF_MPLS_LABEL, mpls_label)
        f_tc = datapath.ofproto_parser.OFPMatchField.make(datapath.ofproto.OXM_OF_MPLS_TC, mpls_tc)

        actions = [datapath.ofproto_parser.OFPActionPushMpls(eth_MPLS),
                   datapath.ofproto_parser.OFPActionSetField(f_label),
                   datapath.ofproto_parser.OFPActionSetField(f_tc),
                   datapath.ofproto_parser.OFPActionSetMplsTtl(mpls_ttl),
                   datapath.ofproto_parser.OFPActionOutput(out_port, 0)]

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(table_id=0,datapath=datapath, priority=priority,out_port=0,out_group=0,match=match, flags=1, instructions=inst)

        datapath.send_msg(mod)

    # Pop mpls flow
    def pop_mpls_flow(self, datapath, priority, match, out_port):

        actions = []

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        eth_IP = ether.ETH_TYPE_IP
        actions = [datapath.ofproto_parser.OFPActionPopMpls(eth_IP),
                   datapath.ofproto_parser.OFPActionOutput(out_port, 0)]

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(table_id=0,datapath=datapath, priority=priority,out_port=0,out_group=0,match=match, flags=1, instructions=inst)

        datapath.send_msg(mod)

    # Push pbb flow
    def push_pbb_flow(self, datapath, priority, match, pbb_isid, pbb_eth_src, pbb_eth_dst, out_port):

        actions = []

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        eth_VLAN = ether.ETH_TYPE_8021Q
        eth_PBB = ether.ETH_TYPE_8021AH
        f_isid = datapath.ofproto_parser.OFPMatchField.make(datapath.ofproto.OXM_OF_PBB_ISID, pbb_isid)
        f_eth_src = datapath.ofproto_parser.OFPMatchField.make(datapath.ofproto.OXM_OF_ETH_SRC, pbb_eth_src)
        f_eth_dst = datapath.ofproto_parser.OFPMatchField.make(datapath.ofproto.OXM_OF_ETH_DST, pbb_eth_dst)
        f_vlan_vid = datapath.ofproto_parser.OFPMatchField.make(datapath.ofproto.OXM_OF_VLAN_VID, 100)

        actions = [datapath.ofproto_parser.OFPActionPushPbb(eth_PBB),
                   datapath.ofproto_parser.OFPActionSetField(f_isid),
                   datapath.ofproto_parser.OFPActionSetField(f_eth_src),
                   datapath.ofproto_parser.OFPActionSetField(f_eth_dst),
                   datapath.ofproto_parser.OFPActionPushVlan(eth_VLAN),
                   datapath.ofproto_parser.OFPActionSetField(f_vlan_vid),
                   datapath.ofproto_parser.OFPActionOutput(out_port, 0)]

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(table_id=0,datapath=datapath, priority=priority,out_port=0,out_group=0,match=match, flags=1, instructions=inst)

        datapath.send_msg(mod)

    # Pop pbb flow
    def pop_pbb_flow(self, datapath, priority, match, out_port):

        actions = []

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        eth_IP = ether.ETH_TYPE_IP
        actions = [datapath.ofproto_parser.OFPActionPopPbb(),
                   datapath.ofproto_parser.OFPActionPopVlan(),
                   datapath.ofproto_parser.OFPActionOutput(out_port, 0)]

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(table_id=0,datapath=datapath, priority=priority,out_port=0,out_group=0,match=match, flags=1, instructions=inst)

        datapath.send_msg(mod)


    # Set meter flow
    def set_meter_flow(self, datapath, meter_id, command, priority, match, out_port):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        actions = [datapath.ofproto_parser.OFPActionOutput(out_port, 0)]

        inst = [parser.OFPInstructionMeter(meter_id=meter_id)]
        inst.extend([parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)])
        mod = parser.OFPFlowMod(datapath=datapath, command=command, priority=priority,
                                out_port=0, out_group=0, match=match, instructions=inst)
        datapath.send_msg(mod)
 
    # Protocol finder
    def find_protocol(self, pkt, name):
        for p in pkt.protocols:
            if hasattr(p, 'protocol_name'):
                if p.protocol_name == name:
                    return p

    # Packets decoder 
    def packet_print(self,pkt):
        # Mac information
        pkt_ethernet = pkt.get_protocol(ethernet.ethernet)
        if pkt_ethernet:
            dst_mac = pkt_ethernet.dst
            src_mac = pkt_ethernet.src
            mac_type = pkt_ethernet.ethertype

            LOG.info("########ethernet information########")
            LOG.info("dst_mac:%s src_mac:%s mac_type:%s" % (dst_mac, src_mac, hex(mac_type)))

        # Vlan information
        pkt_vlan = pkt.get_protocol(vlan.vlan)
        if pkt_vlan:
            vlan_pcp = pkt_vlan.pcp
            vlan_cfi = pkt_vlan.cfi
            vlan_vid = pkt_vlan.vid
            vlan_ethertype = pkt_vlan.ethertype
            LOG.info("\n########Vlan information########")
            LOG.info("vlan_pcp:%s vlan_cfi:%s vlan_vid:%s vlan_ethertype:0x%04x\n",vlan_pcp,vlan_cfi,vlan_vid,vlan_ethertype)

        # IPv4 information
        pkt_ipv4 = pkt.get_protocol(ipv4.ipv4)
        if pkt_ipv4:
            ip_version = pkt_ipv4.version
            ip_header_length = pkt_ipv4.header_length
            ip_tos = pkt_ipv4.tos
            ip_total_length = pkt_ipv4.total_length
            ip_identification = pkt_ipv4.identification
            ip_flags = pkt_ipv4.flags
            ip_offset = pkt_ipv4.offset
            ip_ttl = pkt_ipv4.ttl
            ip_proto = pkt_ipv4.proto
            ip_csum = pkt_ipv4.csum
            ip_src = pkt_ipv4.src
            ip_dst = pkt_ipv4.dst
            ip_length = pkt_ipv4.total_length
            ip_option = pkt_ipv4.option
            LOG.info("########IPv4 information########")
            LOG.info("ip_version:%s ip_header_length:%s tos:%s ip_total_length:%s",ip_version,ip_header_length,ip_tos,ip_total_length)
            LOG.info("ip_identification:%s ip_flags:%s ip_offset:%s ip_ttl:%s",ip_identification,ip_flags,ip_offset,ip_ttl)
            LOG.info("ip_proto:%s ip_csum:%s ip_src:%s ip_dst:%s ip_length:%s",ip_proto,ip_csum,ip_src,ip_dst,ip_length)
            LOG.info("ip_option:%s\n",ip_option)

        # Arp information
        pkt_arp = pkt.get_protocol(arp.arp)
        if pkt_arp:
            arp_hwtype = pkt_arp.hwtype
            arp_proto = pkt_arp.proto
            arp_hlen = pkt_arp.hlen
            arp_plen = pkt_arp.plen
            arp_opcode = pkt_arp.opcode
            arp_src_mac = pkt_arp.src_mac
            arp_dst_mac = pkt_arp.dst_mac
            arp_src_ip = pkt_arp.src_ip
            arp_dst_ip = pkt_arp.dst_ip
            LOG.info("########Arp information########")
            LOG.info("arp_hwtype:%s arp_proto:%s arp_hlen:%s arp_plen:%s",arp_hwtype,arp_proto,arp_hlen,arp_plen)
            LOG.info("arp_opcode:%s arp_src_mac:%s arp_dst_mac:%s",arp_opcode,arp_src_mac,arp_dst_mac)
            LOG.info("arp_dst_ip:%s arp_src_ip:%s\n",arp_dst_ip,arp_src_ip)

        # Tcp information
        pkt_tcp = pkt.get_protocol(tcp.tcp)
        if pkt_tcp:
            tcp_src_port = pkt_tcp.src_port
            tcp_dst_port = pkt_tcp.dst_port
            tcp_seq = pkt_tcp.seq
            tcp_ack = pkt_tcp.ack
            tcp_offset = pkt_tcp.offset
            tcp_bits = pkt_tcp.bits
            tcp_window_size = pkt_tcp.window_size
            tcp_csum = pkt_tcp.csum
            tcp_urgent = pkt_tcp.urgent
            tcp_option = pkt_tcp.option
            LOG.info("########Tcp information########")
            LOG.info("tcp_src_port:%s tcp_dst_port:%s tcp_seq:%s tcp_ack:%s",tcp_src_port,tcp_dst_port,tcp_seq,tcp_ack)
            LOG.info("tcp_offset:%s tcp_bits:%s tcp_window_size:%s tcp_csum:%s",tcp_offset,tcp_bits,tcp_window_size,tcp_csum)
            LOG.info("tcp_urgent:%s tcp_option:%s\n",tcp_urgent,tcp_option)

        # Udp information
        pkt_udp = pkt.get_protocol(udp.udp)
        if pkt_udp:
            udp_src_port = pkt_udp.src_port
            udp_dst_port = pkt_udp.dst_port
            udp_total_length = pkt_udp.total_length
            udp_csum = pkt_udp.csum
            LOG.info("########Udp information########")
            LOG.info("udp_src_port:%s udp_dst_port:%s udp_total_length:%s",udp_src_port,udp_dst_port,udp_total_length)
            LOG.info("udp_csum:%s\n",udp_csum)

        # icmp information
        pkt_icmp = pkt.get_protocol(icmp.icmp)
        if pkt_icmp:
            icmp_type = pkt_icmp.type
            icmp_code = pkt_icmp.code
            icmp_csum = pkt_icmp.csum
            icmp_data = pkt_icmp.data
            LOG.info("########Icmp information########")
            LOG.info("icmp_type:%s icmp_code:%s icmp_csum:%s icmp_data:%s\n",icmp_type,icmp_code,icmp_csum,icmp_data)
           
    # packetIn handler 
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
            if f.header == ofproto_v1_3.OXM_OF_IN_PORT:
                in_port = f.value

        LOG.info("\n########in_port information########")
        LOG.info("in_port:%s\n", in_port)

        # packet information 
        pkt = packet.Packet(msg.data)
        self.packet_print(pkt)
        
        # learn a mac address to avoid FLOOD next time.
        pkt_ethernet = pkt.get_protocol(ethernet.ethernet)
        dst = pkt_ethernet.dst
        src = pkt_ethernet.src
        self.mac_to_port[dpid][src] = in_port

        # output port information
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        LOG.info("########out_port information########")
        LOG.info("out_port:%s\n",out_port)

        # match information
        in_port = 13
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
        out_port = 23
        match = self.set_flow_match(datapath,in_port=in_port, dl_dst=dl_dst, dl_src=dl_src,\
                                            dl_type=dl_type,vlan_vid=vlan_vid,vlan_pcp=vlan_pcp,\
                                            ip_dscp=ip_dscp,ip_ecn=ip_ecn,ip_proto=ip_proto,\
                                            ipv4_src=ipv4_src, ipv4_dst=ipv4_dst,tcp_src=tcp_src,tcp_dst=tcp_dst)
        LOG.info("########match information########")
        print "match:%s\n" % match

        # action information
        out_dl_dst = '22:11:11:11:11:11'
        out_dl_src = '22:00:00:00:00:00'
        actions = self.set_flow_action(datapath,out_port=out_port, dl_dst=out_dl_dst,dl_src=out_dl_src,vlan_vid=4094,vlan_pcp=3)

        LOG.info("########action information########")
        print "actions:%s\n" % actions

        # add or delete flow
        if src == '22:11:11:11:11:11':
            LOG.info("#######add flow########")
            self.set_flow(datapath, table_id=0, match=match, flags=1, command=0, actions=actions)
        elif src == '22:11:11:11:11:12':
            LOG.info("#######delete flow########")
            match_del = self.set_flow_match(datapath,in_port=in_port, dl_dst=dl_dst, dl_src=dl_src)
            self.set_flow(datapath, table_id=0, flags=1, match=match_del, command=3)

        # add or delete group
        if src == '22:11:11:11:11:13':
            LOG.info("#######add group########")
            match_group = self.set_flow_match(datapath,in_port=in_port, dl_dst=dl_dst, dl_src=dl_src,\
                                       dl_type=dl_type,vlan_vid=vlan_vid,vlan_pcp=vlan_pcp,\
                                       ip_dscp=ip_dscp,ip_ecn=ip_ecn,ip_proto=ip_proto,\
                                       ipv4_src=ipv4_src, ipv4_dst=ipv4_dst,tcp_src=tcp_src,tcp_dst=tcp_dst)

            bucket_output = [datapath.ofproto_parser.OFPActionOutput(out_port, 0)]
            bucket = self.set_bucket(datapath, actions=bucket_output)
            self.set_group(datapath, group_id=2239, command=0, buckets=bucket)
            actions = [datapath.ofproto_parser.OFPActionGroup(2239)]
            self.set_flow(datapath, table_id=0, match=match_group, command=0, actions=actions)
        elif src == '22:11:11:11:11:14':
            LOG.info("#######del group########")
            match_group = self.set_flow_match(datapath,in_port=in_port, dl_dst=dl_dst)
            self.set_flow(datapath, table_id=0, command=3, match=match_group)
            bucket_output = []
            bucket = self.set_bucket(datapath, actions=bucket_output)
            self.set_group(datapath, type_=0,group_id=2239, command=datapath.ofproto.OFPGC_DELETE,buckets=bucket)

        # push or pop vlan
        if src == '22:11:11:11:11:15':
            LOG.info("#######add flow <push vlan>########")
            vlan_vid = 1000
            self.push_vlan_flow(datapath, priority=32768, match=match, vlan_vid=vlan_vid, out_port=out_port)
        elif src == '22:11:11:11:11:16':
            LOG.info("#######add flow <pop vlan>########")
            self.pop_vlan_flow(datapath, priority=32769, match=match, out_port=out_port)

        # push or pop mpls
        if src == '22:11:11:11:11:17':
            LOG.info("#######add flow <push mpls>########")
            mpls_label = 20
            mpls_tc = 2
            mpls_ttl = 30
            self.push_mpls_flow(datapath, priority=12345, match=match, mpls_label=mpls_label, mpls_tc=mpls_tc, mpls_ttl=mpls_ttl, out_port=out_port)
        elif src == '22:11:11:11:11:18':
            LOG.info("#######add flow <pop mpls>########")
            self.pop_mpls_flow(datapath, priority=12346, match=match, out_port=out_port)

        # Push or pop pbb
        if src == '22:11:11:11:11:19':
            LOG.info("#######add flow <push pbb>########")
            pbb_isid = 23
            pbb_eth_src = '00:11:22:33:44:55'
            pbb_eth_dst = '00:00:00:22:22:22'
            match_pbb = self.set_flow_match(datapath,in_port=in_port, vlan_vid=100)
            self.push_pbb_flow(datapath, priority=123,match=match_pbb,pbb_isid=pbb_isid,pbb_eth_src=pbb_eth_src,pbb_eth_dst=pbb_eth_dst,out_port=out_port)
        elif src == '22:11:11:11:11:1a':
            LOG.info("#######add flow <pop pbb>########")
            pbb_isid = 23
            dl_type = 0x88e7
            match_pbb = self.set_flow_match(datapath,in_port=in_port, dl_type=dl_type, pbb_isid=pbb_isid)
            self.pop_pbb_flow(datapath, priority=12350, match=match_pbb, out_port=out_port)

        # add or delete drop meter
        if src == '22:11:11:11:11:1b':
            LOG.info("#######add meter <drop>########")
            meter_id = 100
            flags = (ofproto.OFPMF_KBPS|ofproto.OFPMF_STATS)
            bands = [datapath.ofproto_parser.OFPMeterBandDrop(rate=10000000)]
            match_meter = self.set_flow_match(datapath,in_port=in_port, vlan_vid=100)
            self.set_meter(datapath, command=0, flags=flags, meter_id=meter_id, bands=bands)
            self.set_meter_flow(datapath, meter_id=meter_id, command=0, priority=13400,match=match_meter,out_port=out_port)
        elif src == '22:11:11:11:11:1c':
            LOG.info("#######del metere########")
            meter_id = 100
            flags = (ofproto.OFPMF_KBPS|ofproto.OFPMF_STATS)
            bands = [datapath.ofproto_parser.OFPMeterBandDrop(rate=10000000)]
            match_meter = self.set_flow_match(datapath,in_port=in_port)
            self.set_meter(datapath, command=2, flags=flags, meter_id=meter_id, bands=bands)
            self.set_flow(datapath, table_id=0, match=match_meter, command=3)
