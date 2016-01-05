#coding=utf8
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory, Protocol

users ={}
class ChatReciever(LineReceiver):
    '''每个客户端连接有个对应ChatReciever实例 ，有自己的名字，收到消息后发给其他所有客户端
    '''
    def __init__(self):
        self.name = ''
        self.state = "GETNAME"  

    def connectionMade(self):
        self.sendLine("Please input your name: ")           #waiting for input
        
    def lineReceived(self,data):
        global users
        if self.name =='':         #input name
            self.name = data
            self.sendLine("Welcome, %s!" % (self.name))
            users[self.name] = self
            print 'User %s log in !'%data
        else:                            #发送消息
            for (user,protocol1) in users.items():
                msg   = '['+self.name+']'+data
                print msg
                if (self.name != user):
                    protocol1.sendLine(msg)

    def sendAll(self,msg):
        for (user,protocol1) in users.items():
            msg = '['+self.name+']'+ msg
            print msg
            if (self.name != user):
                protocol1.sendLine(msg)

factory = Factory()
factory.protocol = ChatReciever
reactor.listenTCP(8001,factory)
reactor.run()
