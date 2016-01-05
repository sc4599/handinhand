# -*- coding:utf-8 –*-
from twisted.web import server, resource, static
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.protocol import Factory
from twisted.internet import reactor


class TcpServerHandle(LineOnlyReceiver):
    def __init__(self, factory):
        self.factory = factory

    # 刚刚建立到连接时 执行
    def connectionMade(self):
        print 'connectionMade self type=', type(self)
        self.sendLine('welcome to china:')
        self.factory.clients.add(self)  # 新连接添加连接对应的Protocol实例到clients

    def connectionLost(self, reason):
        print 'connectionLost self type=', type(self)
        print 'reason = ', reason
        self.factory.clients.remove(self)  # 连接断开移除连接对应的Protocol实例

    # 接受到消息的时候执行
    def lineReceived(self, line):
        print 'lineReceived self type=', type(self)
        print 'current line is :%s' % line
        # 遍历所有的连接，发送数据
        if line.startswith('doctor:::'):
            print 'I am doctor add to doctors'
            tel = line.split(':::')[1]
            self.factory.addToDoctors(tel,self)
        # for c in self.factory.clients:
        #     c.sendLine(line)


class TcpServerFactory(Factory):
    def __init__(self):
        self.clients = set()  # set集合用于保存所有连接到服务器的客户端
        self.doctors={}
        self.patients={}
    def buildProtocol(self, addr):
        print 'this is buildProtocol addr = ', addr
        return TcpServerHandle(self)

    def addToDoctors(self,tel,instance):
        self.doctors[tel]=instance
        print self.doctors
        print 'current doctor counts = %d'%len(self.doctors)

    def addToPatient(self,tel,instance):
        self.patients[tel]=instance

    def sendToDoctors(self,data):
        for c in self.doctors.values():
            c.sendLine(data)

tfactory = TcpServerFactory()


class ChildSimple(resource.Resource):
    isLeaf = True

    def __init__(self, msg):
        resource.Resource.__init__(self)
        self.msg = msg

    def render_GET(self, request):
        self.sendToAll(self.msg)
        return "Hello, No. %s visitor1!" % self.msg

    def sendToAll(self, msg):
        tfactory.sendToDoctors(msg)



class Simple(resource.Resource):
    def __init__(self):
        resource.Resource.__init__(self)
        self.putChild("", self)

    def render_GET(self, request):
        print 'this is first receive message!!!!'
        # 给所有在线客户发消息
        # self.sendToAll('hello tcp')
        return "Hello, world!"

    def getChild(self, path, request):
        return ChildSimple(path)


print '...starting server.....'
reactor.listenTCP(9080, server.Site(Simple()))
reactor.listenTCP(9081, tfactory)
reactor.run()
