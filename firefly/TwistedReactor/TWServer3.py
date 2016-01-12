# -*- coding:utf-8 –*-
from twisted.web import server, resource, static
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory
from twisted.internet import reactor


class TcpServerHandle(LineReceiver):
    def __init__(self, factory):
        self.factory = factory

    # 刚刚建立到连接时 执行
    def connectionMade(self):
        print '...connectionMade self type=', type(self)
        self.sendLine('...welcome to china:')
        self.factory.clients.add(self)  # 新连接添加连接对应的Protocol实例到clients
        if self in self.factory.doctors:
            self.factory.doctors

    # 连接断开时候 执行
    def connectionLost(self, reason):
        print '...connectionLost self type=', type(self)
        # print '...reason dir= ',(dir(reason))
        # print '...reason __dict__= ',(reason.__dict__)
        # print '...self = ', (id(self))
        self.factory.clients.remove(self)  # 连接断开移除连接对应的Protocol实例
        if self in self.factory.doctors.keys():
            tel = self.factory.doctors[self]
            del self.factory.doctors[self]
            del self.factory.doctorsKV[tel]
            print 'doctor client removed'
        elif self in self.factory.patients.keys():
            tel = self.factory.patients[self]
            del self.factory.patients[self]
            del self.factory.patientsKV[tel]
            print 'patient client removed'

    # 接受消息时候出发此方法。
    # # @line 或得到的消息详细内容
    def dataReceived(self, line):
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
            self.factory.addToPatient(tel, self)
        self.sendLine('succeed')


# tcp服务器工厂， 添加方法，供所有协议调用
class TcpServerFactory(Factory):
    def __init__(self):
        self.clients = set()  # set集合用于保存所有连接到服务器的客户端
        self.doctors = {}
        self.doctorsKV = {}
        self.patients = {}
        self.patientsKV = {}

    # 构造协议对象，并给协议对象添加一个factory属性指向工厂，可以重载
    def buildProtocol(self, addr):
        print '...this is buildProtocol addr = ', addr
        return TcpServerHandle(self)

    # 添加doctor
    def addToDoctors(self, tel, instance):
        self.doctorsKV[tel] = instance
        self.doctors[instance] = tel
        print self.doctors
        print '...current doctor counts = %d' % len(self.doctors)

    # 添加patient
    def addToPatient(self, tel, instance):
        self.patientsKV[tel] = instance
        self.patients[instance] = tel
        print '...current patient counts = %d' % len(self.patients)

    # 向所有医生发消息
    def sendToDoctors(self, data):
        for c in self.doctors.values():
            c.sendLine(data)

    def sendToDoctor(self, tel, data):
        self.doctorsKV.get[tel].sendLine(data)

    def sendToPatient(self, tel, data):
        self.patientsKV.get[tel].sendLine(data)


# 将 factory公有， 让web服务器实现类调用
tfactory = TcpServerFactory()


# http 请求处理类
class Simple(resource.Resource):
    def __init__(self):
        resource.Resource.__init__(self)
        self.putChild("", self)

    # 获取get请求
    def render_GET(self, request):
        print '...this is render_GET !!!!'
        print (request.__dict__)
        doctors = len(tfactory.doctors)
        patients = len(tfactory.patients)
        return "...current online doctors =%d,patients =%d" % (doctors, patients)

    # 获取post请求
    def render_POST(self, request):
        print '...this is render_POST !!!!'
        print (request.__dict__)
        what = request.args.get('what')
        if what == None:
            return '...Please specify the event type...(what ="addTask" or what = "acceptTask")'
        if what == 'addTask':
            # 发布任务
            msg = request.args.get('data')
            self.sendToAllDoctors(msg)
        elif what == 'acceptTask':
            # 医生接受任务
            msg = request.args.get('data')
            tel = request.args.get('tel')
            tfactory.sendToPatient(tel, msg)
        elif what == 'acceptDoctor':
            # 病人选择医生
            tel = request.args.get('tel')
            msg = 'accept'
            tfactory.sendToDoctor(tel,msg)
        elif what == 'unacceptDoctor':
            # 病人选择医生
            tel = request.args.get('tel')
            msg = 'unaccept'
            tfactory.sendToDoctor(tel,msg)
        return '...succeed...'

    # 发送广播给医生
    def sendToAllDoctors(self, msg):
        tfactory.sendToDoctors(msg)




class TCPserverContorl(object):
    def __init__(self, httpPORT=9080, tcpPORT=9081):
        print '...TCPserver listen %d for http...' % httpPORT
        print '...TCPserver listen %d for tcp...' % tcpPORT
        reactor.listenTCP(httpPORT, server.Site(Simple()))
        reactor.listenTCP(tcpPORT, tfactory)

    def runServer(self):
        print '...starting TCPserver.....'
        reactor.run()


if __name__ == '__main__':
    tcpServerContorl = TCPserverContorl()
    tcpServerContorl.runServer()
