# coding:utf8
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import redis
import os
from tornado.options import define, options
import re
from dao import RedisDAO
import threading

# context = None
# def deleteSelectAll():
#     redis_connect = RedisDAO.connect("192.168.1.18")
#     l = redis_connect.keys('hash_doctor_*')
#     pipeline = redis_connect.pipeline()
#     for i in l:
#         pipeline.delete(i)
#     print pipeline.execute()
#
# def hi():
#     print 'hi'
#
# def jisuan(a):
#     if a == '+':
#         print '+'
#     elif a == '-':
#         print '-'
#     else:
#         print 'other'
import urllib, urllib2


def testHttp():
    url = 'http://192.168.1.124:9080/song'
    req = urllib2.Request(url)
    print req

    res_data = urllib2.urlopen(req)
    res = res_data.read()
    print res


def testHttpPOST():
    url = 'http://192.168.1.124:9080/'
    values = {'msg': 'wahaha'}
    post_data = urllib.urlencode(values)
    req = urllib2.Request(url, data=post_data)
    response  = urllib2.urlopen(req)
    res = response.read()
    print res


from time import ctime, sleep

# def loop(nloop, nsec):
#     print 'start loop, ', nloop, 'at:', ctime()
#     sleep(nsec)
#     print 'loop', nloop, 'done at:', ctime()


if __name__ == '__main__':
    testHttpPOST()
