# -*- coding:utf-8 –*-
from twisted.web import server, resource, static
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory
from twisted.internet import reactor
import time
import json
import re

class TcpServerHandle(LineReceiver):
    def __init__(self, factory):
        self.factory = factory

    # 刚刚建立到连接时 执行
    def connectionMade(self):
        print '...connectionMade self type=', type(self)
        self.sendLine('...welcome to china:')
        self.factory.clients.add(self)  # 新连接添加连接对应的Protocol实例到clients

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
            if tel in self.factory.doctorsKV.keys():
                del self.factory.doctorsKV[tel]
            else:
                print '...%s is not in doctorKV at :'%tel,time.ctime(time.time())
            print '...doctor %s client removed' % tel
        elif self in self.factory.patients.keys():
            tel = self.factory.patients[self]
            del self.factory.patients[self]
            del self.factory.patientsKV[tel]
            print 'patient %s client removed' % tel

    # 接受消息时候出发此方法。
    # # @line 或得到的消息详细内容
    def dataReceived(self, line):
        # if line != ' ':
        #     print '...current line is :%s' % line
        # 连接服务器收到  doctor:::15012822291:::msg  这样的格式的信息
        #                  type:::tel:::other
        if line.startswith('doctor:::'):
            tel = line.split(':::')[1]
            p2 = re.compile('^0\d{2,3}\d{7,8}$|^1[3587]\d{9}$|^147\d{8}')
            if tel not in self.factory.patientsKV:
                if p2.match(tel):
                    print '...I am doctor add to doctors tel = %s' % tel
                    self.factory.addToDoctors(tel, self)
                else:
                    print '...pleace input correct phone number'
        elif line.startswith('patient:::'):
            tel = line.split(':::')[1]
            p2 = re.compile('^0\d{2,3}\d{7,8}$|^1[3587]\d{9}$|^147\d{8}')
            if tel not in self.factory.patientsKV:
                if p2.match(tel):
                    print '...I am patient add to patients tel = %s' % tel
                    self.factory.addToPatient(tel, self)
                else:
                    print '...pleace input correct phone number'
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
        print '...',self.doctors
        print '...current doctor counts = %d' % len(self.doctorsKV)

    # 添加patient
    def addToPatient(self, tel, instance):
        self.patientsKV[tel] = instance
        self.patients[instance] = tel
        print self.patientsKV
        print '...current patient counts = %d' % len(self.patientsKV)

    # 向所有医生发消息
    def sendToDoctors(self, data):
        for c in self.doctorsKV.values():
            c.sendLine(data)

    def sendToDoctor(self, tel, data):
        print '...sendToDoctor tel=', tel
        if tel in self.doctorsKV.keys():
            self.doctorsKV.get(tel).sendLine(data)
            return '10001'
        else:
            print '..current doctor', tel, 'not online'
            return '200403'  # 推送目标不在线

    def sendToPatient(self, tel, data):
        entity = self.patientsKV.get(tel)
        print '...', self.patientsKV.get(tel)
        print '...', self.patients.get(self)
        if entity != None:
            print 'befor send data len = ', len(data)
            self.patientsKV.get(tel).sendLine(data)
            return '10001'
        else:
            print '..current patient', tel, 'not online'
            return '200403'  # 推送目标不在线


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
        # print (request.__dict__)
        doctors = len(tfactory.doctorsKV)
        patients = len(tfactory.patientsKV)
        lpatients = ''
        ldoctors = ''
        for i in tfactory.doctorsKV.keys():
            ldoctors = ldoctors+str(i)+','
            print ldoctors
        for i in tfactory.patientsKV.keys():
            lpatients=lpatients+str(i)+','
        j1 = json.dumps(ldoctors)
        j2 = json.dumps(lpatients)
        return "...current online<br> doctors =%d<br>%s<br> patients = %d<br>%s<br>"%(doctors,j1,patients,j2)
        # return "...current online<br> doctors =%d<br>"%doctors,ldoctors,",patients =%d<br>" %  patients,lpatients

    # 获取post请求
    def render_POST(self, request):
        print '...this is render_POST !!!!'
        what = request.args.get('what')[0]
        print '...this is what = %s' % what
        if what == None:
            return '...Please specify the event type...(what ="addTask" or what = "acceptTask")'
        if what == 'addTask':
            # 发布任务
            msg = request.args.get('data')[0]
            print 'this is render_GET msg = ', msg
            self.sendToAllDoctors(msg)
            return '...succeed...addTask'
        elif what == 'acceptTask':
            # 医生接受任务
            msg = request.args.get('data')[0]
            tel = request.args.get('tel')[0]
            print '...this is render_POST acceptTask msg+tel =', msg, tel
            r = tfactory.sendToPatient(tel, msg)
            print '...current push type r = ', r
            return '...succeed...acceptTask'
        elif what == 'acceptDoctor':
            # 病人选择医生
            tel = request.args.get('tel')[0]
            msg = request.args.get('data')[0]
            tfactory.sendToDoctor(tel, msg)
            return '...succeed...acceptDoctor'
        elif what == 'unacceptDoctor':
            # 病人未选择的医生
            tel = request.args.get('tel')[0]
            msg = request.args.get('data')[0]
            tfactory.sendToDoctor(tel, msg)
            return '...succeed...unacceptDoctor'
        elif what == 'deleteAcceptedDoctor':
            # 病人放弃治疗
            tel = request.args.get('tel')[0]
            msg = request.args.get('data')[0]
            r = tfactory.sendToDoctor(tel, msg)
            return r  # '...succeed...deleteAcceptedDoctor'
        elif what == 'confirmTask':
            # 医生确定治疗

            tel = request.args.get('tel')[0]
            msg = request.args.get('data')[0]
            print '...this is render_POST confirmTask msg+tel =', msg, tel
            r = tfactory.sendToPatient(tel, msg)
            return r  # '...succeed...deleteAcceptedDoctor'
        elif what == 'cancelTask':
            # 医生取消为此病人治疗
            tel = request.args.get('tel')[0]
            msg = request.args.get('data')[0]
            r = tfactory.sendToPatient(tel, msg)
            return r  # '...succeed...deleteAcceptedDoctor'
        elif what == 'sendPrivateLetter':
            # 发送私信给医生
            tel = request.args.get('tel')[0]
            print '...this is render_POST tel = ',tel
            msg = request.args.get('data')[0]
            r = tfactory.sendToDoctor(tel, msg)
            print '...sendPrivateLetter!!!!!!!!!!!!!!!!!!!!!'
            return r  # '...succeed...deleteAcceptedDoctor'
        elif what == 'acceptPrivateLetter':
            # 医生取消为此病人治疗
            tel = request.args.get('tel')[0]
            msg = request.args.get('data')[0]
            r = tfactory.sendToPatient(tel, msg)
            return r  # '...succeed...deleteAcceptedDoctor'
        elif what == 'confirmPrivateLetter':
            # 医生取消为此病人治疗
            tel = request.args.get('tel')[0]
            msg = request.args.get('data')[0]
            r = tfactory.sendToPatient(tel, msg)
            return r  # '...succeed...deleteAcceptedDoctor'
        elif what == 'cancelTaskPrivateLetter':
            # 医生取消为此病人治疗
            tel = request.args.get('tel')[0]
            msg = request.args.get('data')[0]
            r = tfactory.sendToPatient(tel, msg)
            return r  # '...succeed...deleteAcceptedDoctor'
        return '...recived msg but unprocesse...'

    # 发送广播给医生
    def sendToAllDoctors(self, msg):
        tfactory.sendToDoctors(msg)

    # 添加子路径
    def getChild(self, path, request):
        return ChildSimple(path)

class ChildSimple(resource.Resource):
    isLeaf = True
    def __init__(self, type):
        self.type = type

    def render_GET(self, request):
        if self.type == 'doctors':
            print '...', self.type,'query current onlien docotr'
            ldoctors = []
            for i in tfactory.doctorsKV.keys():
                ldoctors.append(i)

            return json.dumps(ldoctors)
        elif self.type == 'patients':
            return 'current online patients = 10'

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
