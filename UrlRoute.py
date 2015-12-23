# coding:utf-8
import os

import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options

from dao.RedisDAO import connect
# 获取本机IP
import socket
from control import TaskControl

# 测试数据
testSTR = r"[{id:1,gender:'m',age:20,symptom:'头动脑热',tel:'15012822291',location:{lon:'22.5431720000',lat:'113.9587510000'}}," \
          r"{id:2,gender:'m',age:22,symptom:'风湿类风湿',tel:'13408866736',location:{lon:'22.5425040000',lat:'113.9566850000'}}," \
          r"{id:3,gender:'f',age:22,symptom:'小儿咳嗽',tel:'17093468643',location:{lon:'22.5426540000',lat:'113.9630090000'}}]"

localIP = socket.gethostbyname(socket.gethostname())  # 这个得到本地ip
port = 8002

redisHost = '192.168.1.18'

print "local ip:%s " % localIP

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
        detailTask = {}
        detailTask['symptom'] = symptom
        detailTask['datetime'] = datetime
        detailTask['lat'] = lat
        detailTask['lon'] = lon
        detailTask['patient_name'] = patient_name
        TaskControl.pushTask(detailTask)


class LoginHandler(tornado.web.RequestHandler):
    print 'this is loginHandler'
    def get(self, *args, **kwargs):
        pass

    def post(self, *args, **kwargs):
        username = self.get_argument('username')
        password = self.get_argument('password')

        print username, password


class DetailTaskHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        print(u'开始连接redis。。。')
        r = connect()
        print(u'连接redis成功！！！！！！！！！！')
        p = r.pubsub()
        p.subscribe()
        r.publish('deltailTask', args[0])


# 测试服务器正常运行
class IndexHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write("hello handinhand is  runing...")


# 显示错误代码页面
class ResultCodeHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('result.html')


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
                                              (r'/testPost/', TestPostHandler),
                                              (r'/login/', LoginHandler),
                                              (r'/.*', OtherHandler)
                                              ],
                                    template_path=os.path.join(os.path.dirname(__file__), 'templates'),
                                    **settings)
    httpServer = tornado.httpserver.HTTPServer(myApp)
    httpServer.listen(port)
    print r'server is runing.....at http://%s:%d ' % (localIP, port)
    tornado.ioloop.IOLoop.current().start()
