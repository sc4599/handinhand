# coding = utf-8

from twisted.internet import protocol, reactor
from time import ctime

PORT = 21555


class TSServerProrocol(protocol.Protocol):
    def connectionMade(self):
        global context

        clnt = self.clent = self.transport.getPeer().host
        print '...connected from : %s   on port : %d' % (clnt, PORT)
        self.transport.write('welcome to handinhand')

    def dataReceived(self, data):
        remoteIP = self.clent = self.transport.getPeer().host
        print 'current connection IP = %s ' % remoteIP
        print '         say:%s' % data
        self.transport.write('this is return message [%s] %s' % (ctime(), data))

    def getContext(self):
        return context


if __name__ == '__main__':
    factory = protocol.Factory()
    factory.protocol = TSServerProrocol

    print 'wating for connection...  on port :%d' % PORT
    reactor.listenTCP(PORT, factory)
    reactor.run()
