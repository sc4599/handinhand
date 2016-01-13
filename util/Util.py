# coding:utf8
import os, json

# 获取当前文件夹的绝对路径





# 记录常用属性， redisIP 等。。。
class Config(object):
    def __init__(self):
        # print config
        self.reidsIP = ''
        self.redisPORT = ''
        self.redisAUTH = ''
        self.mysqlIP = ''
        self.mysqlPORT = ''
        self.mysqlUSERNAME = ''
        self.mysqlPASSWORD = ''
        self.mysqlDATABASE = ''
        self.socketIP = ''
        self.socketIPPORT = ''
        self.httpIP = ''
        self.httpPORT = ''
    def getINIT(self):
        path = os.path.dirname(__file__)
        f = open(path + '/config.json')
        config = json.load(f)
        self.reidsIP = config['redis']['ip']
        self.redisPORT = config['redis']['port']
        self.redisAUTH = config['redis']['auth']
        self.mysqlIP = config['mysql']['ip']
        self.mysqlPORT = config['mysql']['port']
        self.mysqlUSERNAME = config['mysql']['username']
        self.mysqlPASSWORD = config['mysql']['password']
        self.mysqlDATABASE = config['mysql']['database']
        self.socketIP = config['socket']['ip']
        self.socketIPPORT = config['socket']['port']
        self.httpIP = config['http']['ip']
        self.httpPORT = config['http']['port']

if __name__ == '__main__':
    c = Config()
    print c.mysqlDATABASE
