from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_4
from ryu.ofproto import ofproto_v1_4_parser
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet

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
 

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
 

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
 

        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        datapath.send_msg(mod)


         
        #self.group_v12(datapath, command=0, type_=datapath.ofproto.OFPGT_INDIRECT, groupid=1, buckets=buckets)

    def bucket_v12(self, datapath, len_=0, weight=0, watch_port=0xffffffff, watch_group=0xffffffff,action=[]):
        buckets = [datapath.ofproto_parser.OFPBucket(len_=len_, weight=weight, watch_port=watch_port,watch_group=watch_group, actions=action)]
        return buckets

    def group_v12(self, datapath, command=0, type_=0, groupid=0, buckets=None):
        group = datapath.ofproto_parser.OFPGroupMod(datapath=datapath,command=command,type_=type_, group_id=groupid, buckets=buckets)
        datapath.send_msg(group)    
    
    def send_bundle_control(self, datapath, bundle_id, type, flags):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
 

        #req = ofp_parser.OFPBundleCtrlMsg(datapath, bundle_id,
                                          #ofp.OFPBCT_OPEN_REQUEST,
                                          #[ofp.OFPBF_ATOMIC], [])
        req = ofp_parser.OFPBundleCtrlMsg(datapath, int(bundle_id), int(type), flags, [])
        datapath.send_msg(req)
 
    def send_bundle_add_message(self, datapath, bundle_id, flags, matchs, output):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
 
        #msg = ofp_parser.OFPRoleRequest(datapath, ofp.OFPCR_ROLE_EQUAL, 0)
        msg = ofp_parser.OFPMatch
 
        cookie = cookie_mask = 0
        table_id = 0
        idle_timeout = hard_timeout = 0
        priority = 32768
        buffer_id = ofp.OFP_NO_BUFFER
        importance = 0
        #match = ofp_parser.OFPMatch(in_port=1, eth_dst='ff:ff:ff:ff:ff:ff')
        actions = [ofp_parser.OFPActionOutput(output, 0)]
        inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS,
                                                    actions)]

        command = 0
        type_=datapath.ofproto.OFPGT_INDIRECT
        groupid=1
        buckets = [datapath.ofproto_parser.OFPActionOutput(2, 0)]
        buckets = self.bucket_v12(datapath, action=buckets)         
        buckets=buckets

        msg = ofp_parser.OFPGroupMod(datapath=datapath,command=command,type_=type_, group_id=groupid, buckets=buckets)
        req = ofp_parser.OFPBundleAddMsg(datapath, int(bundle_id), flags,
                                          msg, [])  
        #datapath.send_msg(req)   
                                                    
        for match in matchs:
           msg = ofp_parser.OFPFlowMod(datapath, cookie, cookie_mask,
                                        table_id, ofp.OFPFC_ADD,
                                        idle_timeout, hard_timeout,
                                        priority, buffer_id,
                                        ofp.OFPP_ANY, ofp.OFPG_ANY,
                                        ofp.OFPFF_SEND_FLOW_REM,
                                        importance,
                                        match, inst)

           #msg = ofp_parser.OFPRoleRequest(datapath, ofp.OFPCR_ROLE_EQUAL, 0)
                                        
           req = ofp_parser.OFPBundleAddMsg(datapath, int(bundle_id), flags,
                                          msg, [])
           datapath.send_msg(req)
           
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        #vid = msg.match['vlan_vid']
 
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
 
        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})
 
        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)
         
        matchs = []
        for vid in range (1, 102):
            match = parser.OFPMatch(vlan_vid=vid, vlan_pcp=2, eth_dst=dst)
            matchs.append(match)
 
        self.send_bundle_control(datapath, 3, ofproto.OFPBCT_OPEN_REQUEST, ofproto.OFPBF_ORDERED)
        #self.send_bundle_control(datapath, 3, ofproto.OFPBCT_OPEN_REQUEST, ofproto.OFPBF_ORDERED)
        #self.send_bundle_add_message(datapath, 3, ofproto.OFPBF_ORDERED, matchs, in_port)
        self.send_bundle_control(datapath, 3, ofproto.OFPBCT_CLOSE_REQUEST, ofproto.OFPBF_ORDERED)
        #self.send_bundle_control(datapath, 3, ofproto.OFPBCT_COMMIT_REQUEST, ofproto.OFPBF_ORDERED)

