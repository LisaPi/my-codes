#*********************************************************************
#
# (C) Copyright Broadcom Corporation 2013-2014
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#*********************************************************************
import ConfigParser
#   This is a script intended
#   to use by Ryu OpenFlow controller
#
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller import dpset
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
#
from ofdpa.config_parser import ConfigParser
from ofdpa.mods import Mods
#
import sys
#
class OfdpaTe(app_manager.RyuApp):

    _CONTEXTS = {'dpset': dpset.DPSet}
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    CONFIG_FILE = 'conf/ofdpa_te.json'

    def __init__(self, *args, **kwargs):
        super(OfdpaTe, self).__init__(*args, **kwargs)
      
    @set_ev_cls(dpset.EventDP, dpset.DPSET_EV_DISPATCHER)
    def handler_datapath(self, ev):
        print "=Event DP="
        print "dpid: %i" % ev.dp.id
        if ev.enter:
            self.build_packets(ev.dp)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        print "=Event PacketIn="

    def build_packets(self, dp):
        #
        config_dir, working_set = ConfigParser.get_working_set(self.CONFIG_FILE)
        #
        for filename in working_set:
            #
            full_filename = config_dir + '/' + filename
            print "------------------------------------------------------------"
            print "processing file: %s" %  full_filename
            print "------------------------------------------------------------"
            #
            config = ConfigParser.get_config(full_filename)
            #
            for type in ConfigParser.get_config_type(config):
                #
                if (type == "flow_mod"):
                    mod_config = ConfigParser.get_flow_mod(config)
                    mod = Mods.create_flow_mod(dp, mod_config)
                    #
                elif (type == "group_mod"):
                    #
                    mod_config = ConfigParser.get_group_mod(config)
                    mod = Mods.create_group_mod(dp, mod_config)

            print "mod len: %i" % sys.getsizeof(mod)
            dp.send_msg(mod)
            print "message sent"

