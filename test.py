# coding:utf8

from dao import RedisDAO

# import urllib, urllib2
#
#
# def testHttp():
#     url = 'http://192.168.1.124:9080/song'
#     req = urllib2.Request(url)
#     print req
#
#     res_data = urllib2.urlopen(req)
#     res = res_data.read()
#     print res
#
#
# def testHttpPOST():
#     url = 'http://192.168.1.124:9080/'
#     values = {'msg': 'wahaha'}
#     post_data = urllib.urlencode(values)
#     req = urllib2.Request(url, data=post_data)
#     response  = urllib2.urlopen(req)
#     res = response.read()
#     print res
#
# def connetRedis():
#     return  RedisDAO.connect('192.168.1.18')
# class test(object):
#     pass

import json
rc =RedisDAO.connect('192.168.1.18')
# r= rc.hgetall('hash_doctor_18818684122')
# l = rc.keys('channel_hash_detailTask_13887083253*')
# s = 'channel_hash_detailTask_13628365645_1452839558'

r = rc.hgetall('hash_doctor_18818684122')
print r.get('current_task_count')
print json.dumps(r.get('current_task_count'))