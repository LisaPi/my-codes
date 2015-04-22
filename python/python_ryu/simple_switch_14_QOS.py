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
from ryu.ofproto import ofproto_v1_4
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
import time

global tim, pt1_sum, pt2_sum, pt3_sum
tim = 0
pt1_sum = pt2_sum = pt3_sum = 0
global pt1_rx1, pt2_rx1, pt3_tx1
global pt1_rx2, pt2_rx2, pt3_tx2
global pt1_rx3, pt2_rx3, pt3_tx3
pt1_rx1 = pt2_rx1 = pt3_tx1 = 0
pt1_rx2 = pt2_rx2 = pt3_tx2 = 0
pt1_rx3 = pt2_rx3 = pt3_tx3 = 0

class SimpleSwitch14(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_4.OFP_VERSION]
    pt1 = 1
    pt2 = 2
    pt3 = 3
    acq_time = 1
    acq_interval = 10
    bandwidth = 100000000
    rsv_bandw = 5000000
    size = 64
    maxpck = (bandwidth-rsv_bandw)/8/(64+8+12)
    
    def __init__(self, *args, **kwargs):
        super(SimpleSwitch14, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install static flow entries
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.
        match = parser.OFPMatch(in_port=self.pt1, eth_src='00:00:00:11:11:11', eth_type=0x0800, ipv4_src='192.168.1.100')
        actions = [parser.OFPActionOutput(self.pt3,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, ofproto.OFPFC_ADD, 1000, match, ofproto.OFPP_ANY, ofproto.OFPG_ANY,actions)
        print("add port1 to port3 flow ok!")

        match = parser.OFPMatch(in_port=self.pt2, eth_src='00:00:00:22:22:22', eth_type=0x0800, ipv4_src='192.168.2.100')
        actions = [parser.OFPActionOutput(self.pt3,
                                          ofproto.OFPCML_NO_BUFFER)]  
        self.add_flow(datapath, ofproto.OFPFC_ADD, 1000, match, ofproto.OFPP_ANY, ofproto.OFPG_ANY,actions)
        print("add port2 to port3 flow ok!")

        #self.meter_mod(datapath, command=ofproto.OFPMC_ADD, flags=ofproto.OFPMF_KBPS, meter_id=1,bands=parser.OFPMeterBandDrop(rate=10000,burst_size=0, type_=None, len_=None))
        bands = [parser.OFPMeterBandDrop(rate=10000)]
        self.meter_mod(datapath, command=ofproto.OFPMC_ADD, flags=(ofproto.OFPMF_KBPS|ofproto.OFPMF_STATS), meter_id=1,bands=bands)
        print("add meter ok!")

        self.SQA_test(datapath)

    def SQA_test(self, datapath):       
        for i in (1,2,3):
            self.send_port_stats_request(datapath)
            time.sleep(self.acq_time)
    
    def add_flow(self, datapath, command, priority, match, outport, outgroup, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,                                        
                                                      actions)]
        mod = parser.OFPFlowMod(datapath=datapath, command=command, priority=priority,
                                out_port=outport, out_group=outgroup, match=match, instructions=inst)
        datapath.send_msg(mod)

    def add_meter_flow(self, datapath, command, priority, match, outport, outgroup, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionMeter(meter_id=1)]
        inst.extend([parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,           
                                                                          actions)])
        mod = parser.OFPFlowMod(datapath=datapath, command=command, priority=priority,
                                out_port=outport, out_group=outgroup, match=match, instructions=inst)
        datapath.send_msg(mod)

    def meter_mod(self, datapath, command=0, flags=0, meter_id=0,bands=[]):
        meter = datapath.ofproto_parser.OFPMeterMod(datapath=datapath,command=command,flags=flags, meter_id=meter_id, 
                                                     bands=bands)
        datapath.send_msg(meter)

    def port_stats_count(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        print('count the pps on ports')
        global pt1_rx1, pt2_rx1, pt3_tx1
        global pt1_rx2, pt2_rx2, pt3_tx2
        global pt1_rx3, pt2_rx3, pt3_tx3
        global pt1_sum, pt2_sum,pt3_sum, tim
        offset_pkt = 100
        print(tim)
        pt1_dif1= (pt1_rx2 - pt1_rx1)/self.acq_time
        print(pt1_dif1)
        pt1_dif2 = (pt1_rx3 - pt1_rx2)/self.acq_time
        print(pt1_dif2)
        pt2_dif1= (pt2_rx2 - pt2_rx1)/self.acq_time
        print(pt2_dif1)
        pt2_dif2 = (pt2_rx3 - pt2_rx2)/self.acq_time
        print(pt2_dif2)
        pt3_dif1= (pt3_tx2 - pt3_tx1)/self.acq_time
        print(pt3_dif1)
        pt3_dif2 = (pt3_tx3 - pt3_tx2)/self.acq_time
        print(pt3_dif2)

        pt1_sum = pt1_dif1 + pt1_dif2
        pt2_sum = pt2_dif1 + pt2_dif2
        pt3_sum = pt3_dif1 + pt3_dif2

        if (float(pt3_sum)/2/self.maxpck > 0.95) & (float(pt1_sum + pt2_sum)/2/self.maxpck > 1.05):
            print("port 3 has congested")
            print(float(pt1_sum + pt2_sum)/2/self.maxpck)
            pt1_p_rate = pt1_sum/2
            if (self.maxpck - pt1_p_rate) <= 0:
                pt2_p_rate = 0
            else:
                pt2_p_rate = self.maxpck - pt1_p_rate
            pt2_kb_rate = pt2_p_rate*self.size*8/1000
            print(pt2_p_rate*self.size*8)
            print("pt2_kb_rate")
            print(pt2_kb_rate)
            bands = [parser.OFPMeterBandDrop(rate=pt2_kb_rate)]
            self.meter_mod(datapath, command=ofproto.OFPMC_MODIFY, flags=(ofproto.OFPMF_KBPS|ofproto.OFPMF_STATS), 
                       meter_id=1, bands=bands)

            match = parser.OFPMatch(in_port=self.pt2, eth_src='00:00:00:22:22:22', eth_type=0x0800, 
                                            ipv4_src='192.168.2.100')       
            actions = [parser.OFPActionOutput(self.pt3,
                                          ofproto.OFPCML_NO_BUFFER)]  
            self.add_meter_flow(datapath, ofproto.OFPFC_MODIFY, 1000, match, ofproto.OFPP_ANY, ofproto.OFPG_ANY,actions)
        else:
            match = parser.OFPMatch(in_port=self.pt2, eth_src='00:00:00:22:22:22', eth_type=0x0800, 
                                   ipv4_src='192.168.2.100')
            actions = [parser.OFPActionOutput(self.pt3,
                                          ofproto.OFPCML_NO_BUFFER)]
            self.add_flow(datapath, ofproto.OFPFC_MODIFY, 1000, match, ofproto.OFPP_ANY, ofproto.OFPG_ANY,actions)

        time.sleep(2)
        self.SQA_test(datapath)
      
    def send_port_stats_request(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def port_stats_reply_handler(self, ev):
        datapath = ev.msg.datapath
        parser = datapath.ofproto_parser
        global pt1_rx1, pt2_rx1, pt3_tx1, tim
        global pt1_rx2, pt2_rx2, pt3_tx2
        global pt1_rx3, pt2_rx3, pt3_tx3
        tim = tim + 1  
        ports = [] 
        for stat in ev.msg.body:          
            ports.append([stat.length, stat.port_no,
                        stat.duration_sec, stat.duration_nsec,                        
                        stat.rx_packets, stat.tx_packets,                    
                        stat.rx_bytes, stat.tx_bytes,                    
                        stat.rx_dropped, stat.tx_dropped,                    
                        stat.rx_errors, stat.tx_errors,                    
                        repr(stat.properties)])          
            if tim%3 == 1:             
                print('The first time to count')      
                if stat.port_no == self.pt1:       
                    print(stat.rx_packets)         
                    pt1_rx1 = stat.rx_packets
                elif stat.port_no == self.pt2:
                    print(stat.rx_packets)
                    pt2_rx1 = stat.rx_packets
                elif stat.port_no == self.pt3:                    
                    print(stat.tx_packets)
                    pt3_tx1 = stat.tx_packets
            elif tim%3 == 2:
                print('The second time to count')        
                if stat.port_no == self.pt1:                                 
                    print(stat.rx_packets)                                      
                    pt1_rx2 = stat.rx_packets  
                elif stat.port_no == self.pt2:                   
                    print(stat.rx_packets)
                    pt2_rx2 = stat.rx_packets
                elif stat.port_no == self.pt3:
                    print(stat.tx_packets)
                    pt3_tx2 = stat.tx_packets
            elif tim%3 == 0:
                print('The third time to count')        
                if stat.port_no == self.pt1:                                 
                    print(stat.rx_packets)                                      
                    pt1_rx3 = stat.rx_packets  
                elif stat.port_no == self.pt2:                   
                    print(stat.rx_packets)
                    pt2_rx3 = stat.rx_packets
                elif stat.port_no == self.pt3:
                    print(stat.tx_packets)
                    pt3_tx3 = stat.tx_packets
        if tim%3 == 0:
            self.port_stats_count(datapath)
