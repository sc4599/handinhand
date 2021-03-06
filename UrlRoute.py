# coding:utf-8
import os
import re
import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options
import time
from dao import MysqlDAO, RedisDAO
from util.Util import Config
# 获取本机IP
import socket
import sys
from control import TaskControl, LoginControl
# 私信控制
from control.PrivateLetterTaskControl import PrivateLetterControl
# 用户控制
from control.UserControl import UserOnLineControl
# 测试数据

localIP = socket.gethostbyname(socket.gethostname())  # 这个得到本地ip
port = 8002
redisHost = '192.168.1.18'
print "local ip:%s " % localIP

# 获取配置文件信息
c = Config()
c.getINIT()
# 与mysql建立连接
db = MysqlDAO.connectMYSQL(c.mysqlIP, c.mysqlDATABASE, c.mysqlUSERNAME, c.mysqlPASSWORD)
# 与 redis 建立连接
redis_connect = RedisDAO.connect(c.reidsIP)
if redis_connect == 'connect failed':
    sys.exit()
ipList = socket.gethostbyname_ex(socket.gethostname())


# 初始化 私信控制器
privateLetterControl = PrivateLetterControl(redis_connect)
# 初始化 用户控制器
getonlineURL= 'http://%s:%s/doctors'%(c.httpIP,c.httpPORT)
userControl = UserOnLineControl(getonlineURL ,redis_connect)


class TestPostHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        pass

    def post(self):
        print(self.request.remote_ip)
        symptom = self.get_argument('symptom')
        datetime = self.get_argument('datetime')
        lat = self.get_argument('lat')
        lon = self.get_argument('lon')
        patient_name = self.get_argument('patient_name')

        print symptom, datetime, lat, lon, patient_name


class LoginHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        pass

    # 接受传递过来的  username 和 password 判断用户名密码是否正确
    # 返回 true 和 false 来判断是否正确
    def post(self, *args, **kwargs):
        username = self.get_argument('username')
        password = self.get_argument('password')
        userType = self.get_argument('userType')
        print u'当前类：LoginHandler', username, password
        r = LoginControl.authUser(redis_connect, username, password, userType)
        print u'当前类：LoginHandler 返回码= ', r
        self.write(r)


class RegisterHandler(tornado.web.RequestHandler):
    '''
    @uerType 用户类型
    @tel 注册电话号码
    @password 密码
    @smscode 接受到的短信验证码
    @:return L{result.html}
    '''

    def get(self, *args, **kwargs):
        pass

    # 接受传递过来的  uerType 和tel, password 和smscode短信验证码
    # 返回 结果码 来判断返回意义
    def post(self, *args, **kwargs):
        userType = self.get_argument('userType')
        tel = self.get_argument('tel')
        password = self.get_argument('password')
        smscode = self.get_argument('smscode')
        entity = {}
        entity['tel'] = tel
        entity['password'] = password

        r = LoginControl.registerPatientOrDoctor(redis_connect, entity, smscode, userType)
        print u'当前类：RegisterHandler', tel, smscode, 'resultcode %s' % r
        self.write(r)


# 更新病人基础信息
class UpdataPatientHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        patient = {}
        patient['tel'] = self.get_argument('tel')
        patient['pic'] = self.get_argument('pic', default=None)
        patient['name'] = self.get_argument('name')
        patient['gender'] = self.get_argument('gender')
        patient['age'] = self.get_argument('age')
        patient['medical_history'] = self.get_argument('medical_history',
                                                       default='list_hash_detailTask_%s' % patient.get('tel'))
        patient['collection_list_id'] = self.get_argument('collection_list_id',
                                                          default='list_collection_%s' % patient.get('tel'))
        r = LoginControl.updataPatientInfo(redis_connect, patient)
        self.write(r)

# 更新医生基础信息
class UpdataDoctorHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        doctor = {}
        doctor['tel']=self.get_argument('tel')
        doctor['age']=self.get_argument('age')
        doctor['pic']=self.get_argument('pic')
        doctor['name']=self.get_argument('name')
        doctor['gender']=self.get_argument('gender')
        doctor['ndividual_resume']=self.get_argument('ndividual_resume',default=None)
        doctor['comment_count']=self.get_argument('comment_count',default=None)
        doctor['grade']=self.get_argument('grade',default=4)
        doctor['adept']=self.get_argument('adept',default=None)
        doctor['treatment_count']=self.get_argument('treatment_count',default=None)
        doctor['qualification_pic']=self.get_argument('qualification_pic',default=None)
        doctor['identification_pic']=self.get_argument('identification_pic',default=None)
        doctor['hospital']=self.get_argument('hospital',default=None)
        doctor['current_task_count']=self.get_argument('current_task_count',default=None)
        r = LoginControl.updataDoctorInfo(redis_connect, doctor)
        self.write(r)

# 修改密码
class FindUserPassword(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        userType = self.get_argument('userType')
        tel = self.get_argument('tel')
        password = self.get_argument('password')
        smsCode = self.get_argument('smsCode')
        r = LoginControl.editPassword(redis_connect,userType,tel,password,smsCode)
        self.write(r)

# 获取当前用户基本信息
class PatientInfoHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        tel = args[0]
        r = LoginControl.getCurrentPatientInfo(redis_connect, tel)
        self.write(r)

# 获取当前用户基本信息
class DoctorInfoHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        tel = args[0]
        r = LoginControl.getCurrentDoctorInfo(redis_connect, tel)
        self.write(r)


# 检查病人当前是否有任务发布
class QueryCurrentTaskHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        tel = args[0]
        r = TaskControl.queryTask(redis_connect, patient_tel=tel)
        self.write(r)

# 根据电话 查询医生当前任务
class QueryAcceptTaskByTelHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        tel = args[0]
        r =TaskControl.queryAcceptTaskByTel(redis_connect,tel)
        self.write(r)

# 测试服务器正常运行
class IndexHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write("hello handinhand is  runing...")


# 显示错误代码页面
class ResultCodeHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('result.html')


class HelpHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('help.html')


# 发送短信验证码
class SendSmscodeHandler(tornado.web.RequestHandler):
    def get(self, *args):
        p2 = re.compile('^0\d{2,3}\d{7,8}$|^1[3587]\d{9}$|^147\d{8}')  # 电话号码匹配正则
        if p2.match(args[0]):
            print 'current method is SendSmscodeHandler--get tel = %s ,connection IP : %s' % (
                args[0], self.request.remote_ip)
            r = LoginControl.sendSmscode(redis_connect, args[0], self.request.remote_ip)  # 获取远程客户端IP
        else:
            r = '200109'  # 电话号码有误
        self.write(r)


class addTaskHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        detailTask = {}
        detailTask['symptom'] = self.get_argument('symptom')
        detailTask['type'] = self.get_argument('type', default='0')
        detailTask['datetime'] = self.get_argument('datetime', default=str(int(time.time())))
        detailTask['lat'] = self.get_argument('lat')
        detailTask['lon'] = self.get_argument('lon')
        detailTask['patient_tel'] = self.get_argument('patient_tel', )
        detailTask['patient_name'] = self.get_argument('patient_name', )
        detailTask['patient_gender'] = self.get_argument('patient_gender', )
        detailTask['patient_age'] = self.get_argument('patient_age', )
        detailTask['blacklist'] = self.get_argument('blacklist', default=None)
        detailTask['doctor_tel'] = self.get_argument('doctor_tel', default='00000000000')
        detailTask['doctor_name'] = self.get_argument('doctor_name', default='无名氏')
        detailTask['user_tel'] = self.get_argument('user_tel', default='朋友电话')
        detailTask['user_addr'] = self.get_argument('user_addr', default='朋友地址')
        detailTask['task_timeout'] = self.get_argument('task_timeout', default='3600')
        detailTask['comment_id'] = self.get_argument('comment_id', default='1')
        r = TaskControl.addTask(redis_connect, detailTask)
        self.write(str(r))


class DeleteTaskHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        detailTaskID = args[0]
        detailTask = dict({'id':detailTaskID})
        r = TaskControl.delectTask(redis_connect,detailTask)
        self.write(r)

class EditTaskHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        detailTask = {}
        detailTask['id'] = self.get_argument('id')
        detailTask['symptom'] = self.get_argument('symptom')
        detailTask['type'] = self.get_argument('type', default='0')
        detailTask['datetime'] = self.get_argument('datetime', default=str(int(time.time())))
        detailTask['lat'] = self.get_argument('lat')
        detailTask['lon'] = self.get_argument('lon')
        detailTask['patient_tel'] = self.get_argument('patient_tel', )
        detailTask['patient_name'] = self.get_argument('patient_name', )
        detailTask['patient_gender'] = self.get_argument('patient_gender', )
        detailTask['patient_age'] = self.get_argument('patient_age', )
        detailTask['doctor_tel'] = self.get_argument('doctor_tel', default='00000000000')
        detailTask['doctor_name'] = self.get_argument('doctor_name', default='无名氏')
        detailTask['user_tel'] = self.get_argument('user_tel', default='朋友电话')
        detailTask['user_addr'] = self.get_argument('user_addr', default='朋友地址')
        detailTask['task_timeout'] = self.get_argument('task_timeout', default='3600')
        detailTask['comment_id'] = self.get_argument('comment_id', default='1')
        r = TaskControl.editTask(redis_connect, detailTask)
        self.write(str(r))


# 查询所有任务接口
class queryAllTaskHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        r = TaskControl.queryAllTask(redis_connect)
        self.write(r)

# 根据ID 查任务的响应医生
class QueryTaskDoctorsByIdHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        detailTaskID = args[0]
        r = TaskControl.queryTaskDoctorsById(redis_connect,detailTaskID)
        self.write(r)

# 根据任务ID 查询任务详细
class QueryTaskInfoById(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        detailTaskID = args[0]
        r = TaskControl.queryTaskInfoById(redis_connect,detailTaskID)
        self.write(r)


# 接受任务接口
class acceptTaskHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        detailTask = {}
        detailTask['id'] = self.get_argument('id')
        detailTask['task_timeout'] = self.get_argument('task_timeout',default=1800)
        detailTask['patient_tel'] = self.get_argument('patient_tel')
        doctor_tel = self.get_argument('doctor_tel')
        r = TaskControl.acceptTask(redis_connect, detailTask, doctor_tel)
        self.write(str(r))

# 暂停和恢复任务过期时间接口
class PauseOrResumeTaskTimeHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        what = args[0]
        detailTaskID = args[1]
        if what =='Pause':
            r = TaskControl.pauseTaskTime(redis_connect,detailTaskID)
        elif what == 'Resume':
            r = TaskControl.resumeTaskTime(redis_connect,detailTaskID)
        else:
            r = '200501'
        self.write(r)


# 接受医生
class AcceptDoctorHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        doctor_tel = self.get_argument('doctor_tel')
        detailTask = {}
        detailTask['id'] = self.get_argument('id')
        r = TaskControl.acceptDoctor(redis_connect, detailTask, doctor_tel)
        self.write(r)


# 病人删除响应医生
class DeleteAcceptedDoctorHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        doctor_tel = self.get_argument('doctor_tel')
        detailTask = {'id':self.get_argument('id')}
        r = TaskControl.deleteAcceptedDoctor(redis_connect,detailTask,doctor_tel)
        self.write(r)

# 医生确定为病人看病
class ConfirmTaskHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        detailTask = {}
        detailTask['id']= self.get_argument('id')
        detailTask['doctor_tel']= self.get_argument('doctor_tel')
        detailTask['patient_tel']= self.get_argument('patient_tel')
        r = TaskControl.confirmTask(redis_connect,detailTask)
        self.write(r)

# 医生取消此任务
class CancelTaskHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        detailTask = {}
        detailTask['id']= self.get_argument('id')
        detailTask['patient_tel']= self.get_argument('patient_tel')
        r =TaskControl.cancelTask(redis_connect,detailTask)
        self.write(r)

# 发送私信
class SendPrivateLetterHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        doctor_tel = self.get_argument('doctor_tel')
        detailTask = {}
        detailTask['symptom'] = self.get_argument('symptom')
        detailTask['type'] = self.get_argument('type', default='0')
        detailTask['datetime'] = self.get_argument('datetime', default=str(int(time.time())))
        detailTask['lat'] = self.get_argument('lat')
        detailTask['lon'] = self.get_argument('lon')
        detailTask['patient_tel'] = self.get_argument('patient_tel', )
        detailTask['patient_name'] = self.get_argument('patient_name', )
        detailTask['patient_gender'] = self.get_argument('patient_gender', )
        detailTask['patient_age'] = self.get_argument('patient_age', )
        detailTask['blacklist'] = self.get_argument('blacklist', default=None)
        detailTask['doctor_tel'] ='00000000000'
        detailTask['doctor_name'] = self.get_argument('doctor_name', default='无名氏')
        detailTask['user_tel'] = self.get_argument('user_tel', default='朋友电话')
        detailTask['user_addr'] = self.get_argument('user_addr', default='朋友地址')
        detailTask['task_timeout'] = self.get_argument('task_timeout', default='3600')
        detailTask['comment_id'] = self.get_argument('comment_id', default='1')
        r = privateLetterControl.sendPrivateLetter(detailTask,doctor_tel)
        self.write(r)

# 医生接受私信
class AcceptPrivateLetterHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        detailTask = {}
        detailTask['id'] = self.get_argument('id')
        detailTask['patient_tel'] = self.get_argument('patient_tel')
        doctor_tel = self.get_argument('doctor_tel')
        r = privateLetterControl.acceptPrivateLetter(detailTask,doctor_tel)
        self.write(r)

# 医生确定接受私信为病人治疗
class ConfirmPrivateLetterHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        detailTask = {}
        detailTask['id'] = self.get_argument('id')
        print self.get_argument('id')
        detailTask['patient_tel'] = self.get_argument('patient_tel')
        detailTask['doctor_tel'] = self.get_argument('doctor_tel')
        r = privateLetterControl.confirmPrivateLetter(detailTask)
        self.write(r)

# 医生取消私信
class CancelTaskPrivateLetterHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        doctor_tel = self.get_argument('doctor_tel')
        detailTask = {}
        detailTask['id'] = self.get_argument('id')
        detailTask['patient_tel'] = self.get_argument('patient_tel')
        r = privateLetterControl.cancelTaskPrivateLetter(detailTask,doctor_tel)
        self.write(r)

# 医生 或 病人 请求自己私信列表
class QueryDoctorPrivateLetterListHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        userType = self.get_argument('userType')
        tel = self.get_argument('tel')
        if userType == 'doctor':
            print 'this is QueryDoctorPrivateLetterListHandler tel=',tel
            r = privateLetterControl.queryDoctorPrivateLetterList(tel)
        elif userType == 'patient':
            r = privateLetterControl.queryPatientPrivateLetterList(tel)
        else:
            r = 'plase confirm userType "doctor"or"patient"'
        self.write(r)

class qiniuHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write('this is qiniuHandler get')

    def post(self, *args, **kwargs):
        msg = self.get_argument('msg')
        etag = self.get_argument('etag')
        fname = self.get_argument('fname')
        print 'callback msg = %s' % msg
        print 'callback etag = %s' % etag
        print 'callback fname = %s' % fname

# 获取当前在线医生
class GetDoctorIfonlineHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write(userControl.getDoctorsOnlineEntity())

# 根据 半径获取半径内 所有医生
class GetDoctorByRadiusHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        lat_a = float(self.get_argument('lat_a'))
        lng_a = float(self.get_argument('lng_a'))
        radius = int(self.get_argument('radius'))
        r = userControl.getDoctorBydistance(radius,lat_a,lng_a)
        self.write(r)

class OtherHandler(tornado.web.RequestHandler):
    print 'this is  OtherHandler'

    def get(self, *args, **kwargs):
        print 'render postTask.html'
        self.render('other.html')


# 启动TCP服务器
def startTcpServer():
    tcpserver = TWServer3.TCPserverContorl()
    tcpserver.runServer()


# 启动web服务器
def startTornadoServer():
    if redis_connect == 'connect failed':
        print 'redis connect failed'
    # 开启 debug 模式
    settings = {'debug': True}
    myApp = tornado.web.Application(handlers=[(r'/', IndexHandler),
                                              (r'/resultCode/', ResultCodeHandler),
                                              (r'/help/', HelpHandler),
                                              (r'/testPost/', TestPostHandler),
                                              (r'/login/', LoginHandler),
                                              (r'/register/', RegisterHandler),
                                              (r'/updataPatient/', UpdataPatientHandler),
                                              (r'/updataDoctor/', UpdataDoctorHandler),
                                              (r'/findUserPassword/', FindUserPassword),
                                              (r'/patientInfo/tel=(.*)', PatientInfoHandler),
                                              (r'/doctorInfo/tel=(.*)', DoctorInfoHandler),
                                              (r'/sendSmscode/tel=(.*)', SendSmscodeHandler),
                                              (r'/addTask/', addTaskHandler),
                                              (r'/deleteTask/id=(.*)', DeleteTaskHandler),
                                              (r'/editTask/', EditTaskHandler),
                                              (r'/queryTask/tel=(.*)', QueryCurrentTaskHandler),
                                              (r'/queryTaskDoctorsById/id=(.*)', QueryTaskDoctorsByIdHandler),
                                              (r'/queryTaskInfoById/id=(.*)', QueryTaskInfoById),
                                              (r'/acceptTask/', acceptTaskHandler),
                                              (r'/pauseOrResumeTaskTime/', PauseOrResumeTaskTimeHandler),
                                              (r'/acceptDoctor/', AcceptDoctorHandler),
                                              (r'/confirmTask/', ConfirmTaskHandler),
                                              (r'/cancelTask/', CancelTaskHandler),
                                              (r'/deleteAcceptedDoctor/', DeleteAcceptedDoctorHandler),
                                              (r'/queryAllTaskHandler/', queryAllTaskHandler),
                                              (r'/queryAcceptTaskByTel/tel=(.*)', QueryAcceptTaskByTelHandler),
                                              (r'/sendPrivateLetter/', SendPrivateLetterHandler),
                                              (r'/acceptPrivateLetter/', AcceptPrivateLetterHandler),
                                              (r'/confirmPrivateLetter/', ConfirmPrivateLetterHandler),
                                              (r'/cancelTaskPrivateLetter/', CancelTaskPrivateLetterHandler),
                                              (r'/queryDoctorPrivateLetterList/', QueryDoctorPrivateLetterListHandler),
                                              (r'/qiniuUp/', qiniuHandler),
                                              (r'/getDoctorIfonline/', GetDoctorIfonlineHandler),
                                              (r'/getDoctorByRadius/', GetDoctorByRadiusHandler),
                                              (r'/.*', OtherHandler)
                                              ],
                                    template_path=os.path.join(os.path.dirname(__file__), 'templates'),
                                    **settings)
    httpServer = tornado.httpserver.HTTPServer(myApp)
    httpServer.listen(port)
    ISOTIMEFORMAT = '%Y-%m-%d %X'
    print r'server is runing.....at %s http://%s:%d ' % (time.strftime(ISOTIMEFORMAT, time.localtime()), localIP, port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    # 启动tcp服务器addToPatient
    from firefly.TwistedReactor import TWServer3
    # 使用线程启动 To rnadoServer
    import threading

    tornadoServerThread = threading.Thread(target=startTornadoServer)
    tornadoServerThread.start()
    # tcpServerThread  = threading.Thread(target=startTcpServer)
    # tcpServerThread.start()
    # tornadoServerThread.join()
    startTcpServer()
