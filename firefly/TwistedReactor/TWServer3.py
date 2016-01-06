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
        print '...connectionMade self type=', type(self)
        self.sendLine('...welcome to china:')
        self.factory.clients.add(self)  # 新连接添加连接对应的Protocol实例到clients

    def connectionLost(self, reason):
        print '...connectionLost self type=', type(self)
        print '...reason = ', reason
        self.factory.clients.remove(self)  # 连接断开移除连接对应的Protocol实例

    # 接受到消息的时候执行
    def lineReceived(self, line):
        print '...lineReceived self type=', type(self)
        print '...current line is :%s' % line
        # 连接服务器收到  doctor:::15012822291:::msg  这样的格式的信息
        #                  type:::tel:::other
        if line.startswith('doctor:::'):
            tel = line.split(':::')[1]
            print '...I am doctor add to doctors tel = %s' % tel
            self.factory.addToDoctors(tel, self)
            # for c in self.factory.clients:
            #     c.sendLine(line)
        elif line.startswith('patient:::'):
            tel = line.split(':::')[1]
            print '...I am patient add to patients tel = %s' % tel
            self.factory.addToPatient(tel,self)
        self.sendLine('succeed')

# tcp服务器工厂， 添加方法，供所有协议调用
class TcpServerFactory(Factory):
    def __init__(self):
        self.clients = set()  # set集合用于保存所有连接到服务器的客户端
        self.doctors = {}
        self.patients = {}

    def buildProtocol(self, addr):
        print '...this is buildProtocol addr = ', addr
        return TcpServerHandle(self)

    def addToDoctors(self, tel, instance):
        self.doctors[tel] = instance
        print self.doctors
        print '...current doctor counts = %d' % len(self.doctors)

    def addToPatient(self, tel, instance):
        self.patients[tel] = instance

    def sendToDoctors(self, data):
        for c in self.doctors.values():
            c.sendLine(data)

# 将 factory公有， 让web服务器实现类调用
tfactory = TcpServerFactory()



# http 请求处理类
class Simple(resource.Resource):
    def __init__(self):
        resource.Resource.__init__(self)
        self.putChild("", self)

    def render_GET(self, request):
        print '...this is render_GET !!!!'
        # 给所有在线客户发消息
        # self.sendToAll('hello tcp')
        return "...Hello, world!"

    def render_POST(self,request):
        print '...this is render_POST !!!!'
        print (request.__dict__)
        msg = request.content.getvalue().split('=')[1]
        # self.sendToAll(msg)
        # print request.args.get('type')[0]
        self.sendToAll(msg)
        return '...succeed...'

    def sendToAll(self, msg):
        tfactory.sendToDoctors(msg)

class TCPserverContorl(object):
    def __init__(self, httpPORT = 9080, tcpPORT = 9081):
        print '...TCPserver listen %d for http...' % httpPORT
        print '...TCPserver listen %d for tcp...' % tcpPORT
        reactor.listenTCP(9080, server.Site(Simple()))
        reactor.listenTCP(9081, tfactory)

    def runServer(self):
        print '...starting TCPserver.....'
        reactor.run()


if __name__ == '__main__':
    tcpServerContorl = TCPserverContorl()
    tcpServerContorl.runServer()
