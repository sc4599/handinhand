# coding:utf8
from dao import MysqlDAO,RedisDAO
from util.Util import Config
import random
# 获取配置文件信息
c = Config()
# 与mysql建立连接
db = MysqlDAO.connectMYSQL(c.mysqlIP,c.mysqlDATABASE,c.mysqlUSERNAME,c.mysqlPASSWORD)
# 与 redis 建立连接
redis_connect = RedisDAO.connect(c.reidsIP)

# return True表示验证失败， False表示验证成功
def authUser(username,password):
    r = MysqlDAO.isExistsPatient(db,username)
    if r != False:
        pwd = r[0]['password']
        if pwd == password:
            return 'true'
        else:
            return 'false'
    else:
        return 'false'

def registerPatient(patient,password,smscode):
    tel = patient.get('tel')
    r = MysqlDAO.isExistsPatient(db,tel)
    r1 = RedisDAO.isExistsPatient(redis_connect,tel)
    if r1 | r:
        return '200101' # 该用户已经存在
    else:
        if authSmscode(tel,smscode):
            RedisDAO.redisSavePatient(patient)

def updataPatientInfo(patient):
    RedisDAO.redisSavePatient(redis_connect,patient)


# 发送验证码
def sendSmscode(tel):
    # todo 注意恶意刷短信
    smscode = int(random.uniform(1000,9999))
    redis_connect.set('smscode_%s'%tel,smscode,ex=60)
    # todo send smscode to smsdata

# 验证短信验证码是否成功
def authSmscode(tel,smscode):
    code = redis_connect.get('smscode_%s'%tel)
    if code == smscode:
        return True
    else:
        return False