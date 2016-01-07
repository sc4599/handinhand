# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
客户端的几个事件响应
startConnecting 正在连接服务器
buildProtocol 已连接上服务器，创建Protocol
clientConnectionLost 与主机失去连接
clientConnectionFailed　与主机连接失败
添加自动连接功能，当连接主机失败后；再次进行连接
当与主机连接失败后，再次进行连接；
"""
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet import reactor
from sys import stdout


class Echo(LineOnlyReceiver):
    # def dataReceived(self, data):
    #     print data
    #     print (self.dataReceived.__dict__)
    #     print dir(self.transport.__dict__)
    # 接受到消息的时候执行
    def lineReceived(self, line):
        print 'this is lineReceived'
        print line
        if line != 'succeed':
            self.sendLine('doctor:::15012822291:::msg')
        else:
            pass

class EchoClientFactory(ClientFactory):
    def startedConnecting(self, connector):
        print("Start to connect")

    def buildProtocol(self, addr):
        print("build protocol")

        return Echo()

    def clientConnectionLost(self, connector, reason):
        print("client connection lost" + str(reason))
        # 与主机断开连接后，将自动进行连接
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print("client connection failed" + str(reason))
        # 当连接失败后，自动进行连接
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)



reactor.connectTCP("192.168.1.124", 9081, EchoClientFactory())
reactor.run()
