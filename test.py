# coding:utf8
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import redis
import os
from tornado.options import define, options
import re



if __name__ == "__main__":
    d = {'name':'songchao','age':'22'}
    d2 = {'name':'songchao1','age':'23'}
    d3 = {'name':'songchao3','age':'24'}
    l=[]
    l.append(d)
    l.append(d2)
    l.append(d3)

    import json

    print json.dumps(l)