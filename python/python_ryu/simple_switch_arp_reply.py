from ryu.base import app_manager
from ryu.controller import ofp_event, dpset
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls

class TestApp(app_manager.RyuApp):
    def __init__(self, *args, **kwargs):
        super(TestApp, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        print 'packet in'

    @set_ev_cls(dpset.EventDP, dpset.DPSET_EV_DISPATCHER)
    def datapath_handler(self, ev):
        dp = ev.dp
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        if ev.enter:
            cmd = ofp.OFPFC_ADD
            match = ofp_parser.OFPMatch(eth_dst='08:9e:01:a7:dd:d8',
                                        eth_type=0x0806,
                                        in_port=1)
            actions = [ofp_parser.OFPActionOutput(ofp.OFPP_CONTROLLER, 0xFFFF)]
            inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS,
                actions)]
            m = ofp_parser.OFPFlowMod(datapath=dp,
                    cookie=0,
                    cookie_mask=0,
                    table_id=0,
                    command=cmd,
                    match=match,
                    instructions=inst)
            dp.send_msg(m)
