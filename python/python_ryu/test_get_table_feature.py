from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller import dpset
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import DEAD_DISPATCHER, HANDSHAKE_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.exception import RyuException
from ryu.ofproto import ofproto_v1_3
from ryu.lib import addrconv, hub
from ryu import utils


class GetTableFeaturesApp(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(GetTableFeaturesApp, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def switch_state_handler(self, ev):
        datapath = ev.datapath
        parser = datapath.ofproto_parser

        if ev.state == MAIN_DISPATCHER:
            req = parser.OFPTableFeaturesStatsRequest(datapath, 0)
            datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPTableFeaturesStatsReply, MAIN_DISPATCHER)
    def table_features_stats_reply_handler(self, ev):
        """
        actually it may reply multiple times because it's a multipart message.
        """
        print ev.msg

    @set_ev_cls(ofp_event.EventOFPErrorMsg,
                [HANDSHAKE_DISPATCHER, CONFIG_DISPATCHER, MAIN_DISPATCHER])
    def error_msg_handler(self, ev):
            msg = ev.msg
            self.logger.debug('OFPErrorMsg received: type=0x%02x code=0x%02x '
                              'message=%s',
                              msg.type, msg.code, utils.hex_array(msg.data))
