# coding:utf8
from dao import MysqlDAO,RedisDAO

import random

# return True表示验证失败， False表示验证成功
def authUser(redis_connect,username,password):
    r = RedisDAO.isExistsPatient(redis_connect,username)
    if r != False:
        pwd = r[0]['password']
        if pwd == password:
            return 'true'
        else:
            return 'false'
    else:
        return 'false'

# 注册病人
# patient 病人实体 dict
# smscode 短信验证码
# userType 用户类型，判断是医生注册还是病人注册
# 返回值 L{templates/result.html}
def registerPatientOrDoctor(redis_connect,entity,smscode,userType):
    tel = entity.get('tel')
    r = RedisDAO.isExistsPatient(redis_connect,tel)
    if r :
        return '200101' # 该用户已经存在
    else:
        if authSmscode(tel,smscode):
            if userType == 'patient':
                rcode = RedisDAO.redisSavePatient(redis_connect,entity)
            else:
                rcode = RedisDAO.redisSaveDoctor(redis_connect,entity)
            if '200200' == rcode:
                return '200102' # 用户注册成功
            else:
                print 'rcode = %s'%rcode
                return '200103' # 用户注册失败
        else:
            return '200104' # 短信验证码错误

# 完善资料
def updataPatientInfo(redis_connect,patient):
    RedisDAO.redisSavePatient(redis_connect,patient)


# 发送验证码
def sendSmscode(redis_connect,tel):
    # todo 注意恶意刷短信
    smscode = int(random.uniform(1000,9999))
    redis_connect.set('smscode_%s'%tel,smscode,ex=60)
    # todo send smscode to smsdata
    s= u' 您的电话是 %s,快约医生验证码 ： %s'%(tel,smscode)
    print s
    return s

# 验证短信验证码是否成功
def authSmscode(redis_connect,tel,smscode):
    code = redis_connect.get('smscode_%s'%tel)
    if code == smscode:
        return True
    else:
        return False