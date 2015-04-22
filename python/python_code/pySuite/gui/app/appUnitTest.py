#!/usr/bin/python 
# -*- coding: utf-8 -*-

'''
Created on 2014-10-09
@author: beyondzhou
@name: appUnitTest.py
@warning: the script can only run at Windows(cmd/python appUnitTest.py)
'''

baseDir = 'E:\Pica8\eclipse\workspace\Gui'
import sys
sys.path.append(r'%s/module' % baseDir)

import unittest
import HTMLTestRunner
import bridgeAddCheck
import bridgeBasicInfo
import bridgeDelCheck
import bridgeEditCheck
import controllerAddCheck
import controllerDelCheck
import controllerEditCheck
import flowsAddIntoBridge
import groupTableAddIntoBridge
import groupTableDelOfBridge
import meterAddIntoBridge
import meterDelOfBridge
import netFlowAddIntoBridge
import netFlowDelOfBridge
import netFlowEditOfBridge
import ovsServerVswitchd
import portAddIntoBridge
import sFlowAddIntoBridge
import sFlowDelOfBridge
import sFlowEditOfBridge

class appUnitTest(unittest.TestCase):
    
    def test_bridgeAddCheck(self):
        bridgeAddCheck.bridgeAddCheck()
        print 'bridgeAddCheck test done!'

    def test_bridgeBasicInfo(self):
        bridgeBasicInfo.bridgeBasicInfo()
        print 'bridgeBasicInfo test done!'
        
    def test_bridgeDelCheck(self):
        bridgeDelCheck.bridgeDelCheck()
        print 'bridgeDelCheck test done!'
        
    def test_bridgeEditCheck(self):
        bridgeEditCheck.bridgeEditCheck()
        print 'bridgeEditCheck test done!'
        
    def test_controllerAddCheck(self):
        controllerAddCheck.controllerAddCheck()
        print 'controllerAddCheck test done!'
        
    def test_controllerDelCheck(self):
        controllerDelCheck.controllerDelCheck()
        print 'controllerDelCheck test done!'

    def test_controllerEditCheck(self):
        controllerEditCheck.controllerEditCheck()
        print 'controllerEditCheck test done!'
        
    def test_flowsAddIntoBridge(self):
        flowsAddIntoBridge.flowsAddIntoBridge()
        print 'flowsAddIntoBridge test done!'
        
    def test_groupTableAddIntoBridge(self):
        groupTableAddIntoBridge.groupTableAddIntoBridge()
        print 'groupTableAddIntoBridge test done!'
        
    def test_groupTableDelOfBridge(self):
        groupTableDelOfBridge.groupTableDelOfBridge()
        print 'groupTableDelOfBridge test done!'

    def test_meterAddIntoBridge(self):
        meterAddIntoBridge.meterAddIntoBridge()
        print 'meterAddIntoBridge test done!'

    def test_meterDelOfBridge(self):
        meterDelOfBridge.meterDelOfBridge()
        print 'meterDelOfBridge test done!'
        
    def test_netFlowAddIntoBridge(self):
        netFlowAddIntoBridge.netFlowAddIntoBridge()
        print 'netFlowAddIntoBridge test done!'
        
    def test_netFlowDelOfBridge(self):
        netFlowDelOfBridge.netFlowDelOfBridge()
        print 'netFlowDelOfBridge test done!'
        
    def test_netFlowEditOfBridge(self):
        netFlowEditOfBridge.netFlowEditOfBridge()
        print 'netFlowEditOfBridge test done!'
        
    def test_ovsServerVswitchd(self):
        ovsServerVswitchd.ovsServerVswithd()
        print 'ovsServerVswitchd test done!'

    def test_portAddIntoBridge(self):
        portAddIntoBridge.portAddIntoBridge()
        print 'portAddIntoBridge test done!'
        
    def test_sFlowAddIntoBridge(self):
        sFlowAddIntoBridge.sFlowAddIntoBridge()
        print 'sFlowAddIntoBridge test done!'
        
    def test_sFlowDelOfBridge(self):
        sFlowDelOfBridge.sFlowDelOfBridge()
        print 'sFlowDelOfBridge test done!'
        
    def test_sFlowEditOfBridge(self):
        sFlowEditOfBridge.sFlowEditOfBridge()
        print 'sFlowEditOfBridge test done!'
                        
if __name__ == "__main__":
    
    filename ="%s/ovsGuiTest.html" % baseDir
    fp = file(filename,"wb")
    suite = unittest.TestSuite()
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(appUnitTest))
    runner = HTMLTestRunner.HTMLTestRunner(stream=fp,title="Report_title",description="Ovs Gui test report")
    runner.run(suite)