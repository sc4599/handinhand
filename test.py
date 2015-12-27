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

def deleteSelectAll():
    redis_connect = RedisDAO.connect("192.168.1.18")
    l = redis_connect.keys('hash_doctor_*')
    pipeline = redis_connect.pipeline()
    for i in l:
        pipeline.delete(i)
    print pipeline.execute()

def hi():
    print 'hi'

if __name__ == "__main__":
    d = {'name':'songchao','age':'22'}
    d2 = {'name':'songchao1','age':'23'}
    d3 = {'name':'songchao3','age':'24'}
    l=[]
    l.append(d)
    l.append(d2)
    l.append(d3)


    threading.Timer(10000,hi())
