import unittest
import time
import sys

sys.path.append("/OVSWebTestAuto")

from OVSWebTestAuto import OVSWebLoginTest
from OVSWebTestAuto import OVSWebAddbrTest

#import OVSWebLoginTest, OVSWebAddbrTest
import HTMLTestRunner

testunit=unittest.TestSuite()

testunit.addTest(unittest.makeSuite(OVSWebLoginTest.OVSWebLoginTest))
testunit.addTest(unittest.makeSuite(OVSWebAddbrTest.OVSWebAddbrTest))

#runner = unittest.TextTestRunner()
#runner.run(testunit)

now = time.strftime("%Y-%m-%d--%H_%M_%S",time.localtime(time.time()))

#filename = 'D:\\selenium_python\\report\\result2.html'
filename = "/home/irong/python/OVSWebTest/report/"+now+'result.html'
fp = file(filename, 'wb')

runner =HTMLTestRunner.HTMLTestRunner(
  stream=fp,
  title=u'OVSWebTest',
  description=u'The test result:')

runner.run(testunit)
