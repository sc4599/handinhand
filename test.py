# coding:utf8
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import redis
import os
from tornado.options import define, options

define("port", default=8001, help="run on the given port", type=int)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("hello")


class SendTaskHandler(object):
    def get(self, *args, **kwargs):
        print(u'开始连接redis 。。。')
        r = redis.StrictRedis(host='192.168.1.18', port='6379', db=0)
        # TODO 是否连接功成未判定
        if r.ping():
            print(type(r))
            print(u'连接redis成功！！！！！！！！！！')
            # print(r.set('name', 'sylar'))
            # print(r.get('name'))
            p = r.pubsub()
            # p.subscribe('1111')
            p.subscribe()
            # for message in p.listen():
            #     print(message)
            r.publish('1111', args[0])
            print u'消息发送完毕'
        else:
            print u'连接redis异常'


class OtherHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        raise tornado.web.HTTPError(status_code=406, log_message='testing', reason=u'您找的页面飞到火星上去了')

class MyApplication(tornado.web.Application):
    def __init__(self):
        handlers = [
            # (r'/', MainHandler),
            (r'/SendTaskHandler/msg=(.*)', SendTaskHandler),  # @app.route('/test1/page=<page>')   ::::::::
            (r'/.*', OtherHandler),  # @错误页面:::
        ]
        settings = {
            'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
            'title': 'this is tornados demo',
            'name': 'songchao',
        }
        super(MyApplication, self).__init__(handlers, **settings)


if __name__ == "__main__":
    # app = make_app()
    # app.listen(8888)
    # 使用自定义都myApplication 创建httpserver
    http_server = tornado.httpserver.HTTPServer(MyApplication())
    # 监听8888端口
    http_server.listen(8888)
    # 启动事件轮循
    tornado.ioloop.IOLoop.current().start()
