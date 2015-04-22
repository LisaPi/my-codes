#!/usr/bin/env python

# tsTclntTW.py

from twisted.internet import protocol, reactor

HOST = 'localhost'
PORT = 21567

class TSClnetProtocol(protocol.Protocol):
    def sendData(self):
        data = raw_input('> ')
        if data:
            print '...sending %s...' % data
            self.transport.write(data)
        else:
            self.transport.loseConnection()

    def connectionMade(self):
        self.sendData()

    def dataReceived(self, data):
        print data
        self.sendData()

class TSClnetFactory(protocol.ClientFactory):
    protocol = TSClnetProtocol
    clientConnectionLost = clientConnectionFailed = \
      lambda self, connector, reason: reactor.stop()

reactor.connectTCP(HOST, PORT, TSClnetFactory())
reactor.run()
