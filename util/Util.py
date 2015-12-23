# coding:utf8
import os,json

#获取当前文件夹的绝对路径
path = os.path.dirname(__file__)
print path
f = open(path+'/config.json')
print f
# 记录常用属性， redisIP 等。。。
class Config(object):
    def __init__(self):
        config = json.load(f)
        print config
        self.reidsIP = config['redis']['ip']
        self.redisPORT = config['redis']['port']
        self.redisAUTH = config['redis']['auth']
        self.mysqlIP = config['mysql']['ip']
        self.mysqlPORT = config['mysql']['port']
        self.mysqlUSERNAME = config['mysql']['username']
        self.mysqlPASSWORD = config['mysql']['password']
        self.mysqlDATABASE = config['mysql']['database']

if __name__ == '__main__':
    c = Config()
    print c.mysqlDATABASE