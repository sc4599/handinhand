# coding:utf8
from dao import MysqlDAO, RedisDAO
import json
import random

debugtest = True

# return True表示验证失败， False表示验证成功
def authUser(redis_connect, username, password,userType):
    if debugtest:
        print 'authUser ing.. current user is %s'%userType
    r = RedisDAO.isExistsPatientOrDoctor(redis_connect, username,userType)
    if r=='200201':
        return '200201'# 提交的用户类型错误
    if r :
        pwd = RedisDAO.redisQueryPatientOrDoctorPWD(redis_connect,username,userType)
        print u'当前密码 ： %s'% pwd
        if password == pwd:
            return '200202'  # 登录成功
        else:
            return '200203'  # 帐号或密码错误
    else:
        return '200204'  # 用户不存在


# 注册病人
# patient 病人实体 dict
# smscode 短信验证码
# userType 用户类型，判断是医生注册还是病人注册
# 返回值 L{templates/result.html}
def registerPatientOrDoctor(redis_connect, entity, smscode, userType):
    tel = entity.get('tel')
    r = RedisDAO.isExistsPatientOrDoctor(redis_connect, tel,userType)
    if r:
        return '200101'  # 该用户已经存在
    else:
        if authSmscode(redis_connect, tel, smscode):
            if userType == 'patient':
                redis_connect.hset('hash_userInfo','hash_patient_%s'%tel,entity.get('password'))
                rcode = RedisDAO.redisSavePatient(redis_connect, entity)
            elif userType == 'doctor':
                redis_connect.hset('hash_userInfo','hash_doctor_%s'%tel,entity.get('password'))
                rcode = RedisDAO.redisSaveDoctor(redis_connect, entity)
            else:
                return '200201'  # 提交用户类型错误
            if '200200' == rcode:
                return '200102'  # 用户注册成功
            else:
                print 'rcode = %s' % rcode
                return '200103'  # 用户注册失败
        else:
            return '200104'  # 短信验证码错误


# 完善资料
def updataPatientInfo(redis_connect, patient):
    return RedisDAO.redisSavePatient(redis_connect, patient)

def updataDoctorInfo(redis_connect, doctor):
    return RedisDAO.redisSaveDoctor(redis_connect, doctor)

def editPassword(redis_connect,userType,tel,password,smsCode):
    # 1.查看此用户是否注册过
    if RedisDAO.isExistsPatientOrDoctor(redis_connect, tel,userType):
        return '200101'  # 该用户已经存在
    # 2.核对验证码是否正确
    if authSmscode(redis_connect,tel,smsCode) == False:
        return '200104' # 验证码错误
    # 3.以上都没有问题   则修改密码
    if userType == 'patient':
        r=redis_connect.hset('hash_userInfo','hash_patient_%s'%tel,password)
    elif userType == 'doctor':
        r=redis_connect.hset('hash_userInfo','hash_doctor_%s'%tel,password)
    return '10010' # 修改密码成功


# 获取当前用户信息
def getCurrentPatientInfo(redis_connect,tel):
    print '%s getCurrentPatientInfo'%tel
    r = redis_connect.hgetall('hash_patient_%s'%tel)
    if r:
        return json.dumps(r)
    else:
        return '200107' # 查无此用户

# 获取当前用户信息
def getCurrentDoctorInfo(redis_connect,tel):
    print '%s getCurrentPatientInfo'%tel
    r = redis_connect.hgetall('hash_doctor_%s'%tel)
    if r:
        return json.dumps(r)
    else:
        return '200107' # 查无此用户
# 发送验证码
def sendSmscode(redis_connect, tel,remoteIP):
    # todo 注意同一IP恶意刷短信

    # 同一号码 60秒内无法重复注册
    if redis_connect.exists('smscode_%s' % tel):
        return '200105' # 验证码已发送，请稍候

    smscode = int(random.uniform(1000, 9999))
    redis_connect.set('smscode_%s' % tel, smscode, ex=60)  # 将短信验证码写入 redis
    # todo send smscode to smsdata
    s = u' 您的电话是 %s,快约医生验证码 ： %s' % (tel, smscode)
    print s
    return s


# 验证短信验证码是否成功
def authSmscode(redis_connect, tel, smscode):
    code = redis_connect.get('smscode_%s' % tel)  # 查询之前写入的 验证码
    if code == smscode:
        return True
    else:
        return False
