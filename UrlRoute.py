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
from control import TaskControl
from control import LoginControl
# 测试数据
testSTR = r"[{id:1,gender:'m',age:20,symptom:'头动脑热',tel:'15012822291',location:{lon:'22.5431720000',lat:'113.9587510000'}}," \
          r"{id:2,gender:'m',age:22,symptom:'风湿类风湿',tel:'13408866736',location:{lon:'22.5425040000',lat:'113.9566850000'}}," \
          r"{id:3,gender:'f',age:22,symptom:'小儿咳嗽',tel:'17093468643',location:{lon:'22.5426540000',lat:'113.9630090000'}}]"

localIP = socket.gethostbyname(socket.gethostname())  # 这个得到本地ip
port = 8002
redisHost = '192.168.1.18'
print "local ip:%s " % localIP

# 获取配置文件信息
c = Config()
# 与mysql建立连接
db = MysqlDAO.connectMYSQL(c.mysqlIP, c.mysqlDATABASE, c.mysqlUSERNAME, c.mysqlPASSWORD)
# 与 redis 建立连接
redis_connect = RedisDAO.connect(c.reidsIP)

ipList = socket.gethostbyname_ex(socket.gethostname())
for i in ipList:
    if i != localIP:
        print "external IP:%s" % i


class TestPostHandler(tornado.web.RequestHandler):
    print 'this is test post handler'

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
    print 'this is loginHandler'

    def get(self, *args, **kwargs):
        pass

    # 接受传递过来的  username 和 password 判断用户名密码是否正确
    # 返回 true 和 false 来判断是否正确
    def post(self, *args, **kwargs):
        username = self.get_argument('username')
        print username
        password = self.get_argument('password')
        print u'当前类：LoginHandler', username, password
        r = LoginControl.authUser(redis_connect, username, password)
        self.write(r)


class RegisterHandler(tornado.web.RequestHandler):
    '''
    @uerType 用户类型
    @tel 注册电话号码
    @password 密码
    @smscode 接受到的短信验证码
    @:return L{result.html}
    '''
    print 'this is RegisterHandler'

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
        print u'当前类：RegisterHandler', tel, smscode, 'resultcode %s'%r
        self.write(r)


class DetailTaskHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        pass

        # print(u'开始连接redis。。。')
        # r = connect()
        # print(u'连接redis成功！！！！！！！！！！')
        # p = r.pubsub()
        # p.subscribe()
        # r.publish('deltailTask', args[0])

    def post(self, *args, **kwargs):
        detailTask = {}
        detailTask['symptom'] = self.get_argument('symptom')
        detailTask['type'] = self.get_argument('type')
        detailTask['datetime'] = int(time.time())
        detailTask['lat'] = self.get_argument('lat')
        detailTask['lon'] = self.get_argument('lon')
        detailTask['patient_tel'] = self.get_argument('patient_tel')
        detailTask['patient_name'] = self.get_argument('patient_name')
        TaskControl.addTask(redis_connect,detailTask)

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


class SendSmscodeHandler(tornado.web.RequestHandler):
    def get(self, *args):
        p2=re.compile('^0\d{2,3}\d{7,8}$|^1[3587]\d{9}$|^147\d{8}') # 电话号码匹配正则
        if p2.match(args[0]):
            print 'current method is SendSmscodeHandler--get tel = %s' % args[0]
            r = LoginControl.sendSmscode(redis_connect, args[0])
            print self.request.remote_ip  # 获取远程客户端IP
        else:
            r = '200105' #电话号码有误
        self.write(r)


class OtherHandler(tornado.web.RequestHandler):
    print 'this is  OtherHandler'

    def get(self, *args, **kwargs):
        print 'render postTask.html'
        self.render('login.html')


if __name__ == '__main__':
    # 开启 debug 模式
    settings = {'debug': True}
    myApp = tornado.web.Application(handlers=[(r'/', IndexHandler),
                                              (r'/detailTask/msg=(.*)', DetailTaskHandler),
                                              (r'/resultCode/', ResultCodeHandler),
                                              (r'/help/', HelpHandler),
                                              (r'/testPost/', TestPostHandler),
                                              (r'/login/', LoginHandler),
                                              (r'/register/', RegisterHandler),
                                              (r'/sendSmscode/tel=(.*)', SendSmscodeHandler),
                                              (r'/.*', OtherHandler)
                                              ],
                                    template_path=os.path.join(os.path.dirname(__file__), 'templates'),
                                    **settings)
    httpServer = tornado.httpserver.HTTPServer(myApp)
    httpServer.listen(port)
    print r'server is runing.....at http://%s:%d ' % (localIP, port)
    tornado.ioloop.IOLoop.current().start()
