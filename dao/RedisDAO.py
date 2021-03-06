# coding:utf8
import redis
import json

globalsR = None


def connect(redisIP=None, post=6379, db=0, password='songchao'):
    print(u'准备连接redis。。。IP = %s' % redisIP)
    redis_connect = redis.StrictRedis(host=redisIP, port=post, db=db, password=password, charset='utf-8',
                                      decode_responses=True)
    print redis_connect
    print(u'开始连接redis。。。')
    try:
        redis_connect.ping()
        print(u'connect redis  succeesd！！！！！！！！！！')
        return redis_connect
    except:
        print(u'connect redis Failure ！！！！！！！！！！')
        return 'connect failed'


# 存储任务到redis中
def saveDetailTask(redis_connect, detailTask):
    r = redis_connect
    taskid = "hash_tasks_%s" % detailTask.get('id')
    r.hmset(taskid, detailTask)
    print u'储存完毕'
    return '200200'  # 数据写入成功


# 查询当前频道所有任务
# return json 格式的所有任务
def queryChannelTask(redis_connect):
    r = redis_connect.keys('channel_hash_detailTask*')
    l = []
    for e in r:
        rh = redis_connect.hgetall(e)
        l.append(rh)
    return json.dumps(l)


# 根据医生电话查询医生详细信息
# return json格式 的医生实体信息
def queryDoctorByTel(redis_connect, tel):
    r = redis_connect.keys('hash_doctor_%s' % tel)
    return json.dumps(r)


# 储存病人资料到redis中
def redisSavePatient(redis_connect, patient):
    r = redis_connect
    patientid = "hash_patient_%s" % patient.get('tel')
    r.hset(patientid, 'tel', patient.get('tel'))
    r.hset(patientid, 'pic', patient.get('pic'))
    r.hset(patientid, 'name', patient.get('name'))
    r.hset(patientid, 'gender', patient.get('gender'))
    r.hset(patientid, 'age', patient.get('age'))
    r.hset(patientid, 'treatment_count', patient.get('treatment_count'))
    r.hset(patientid, 'colliction_list_id', patient.get('colliction_list_id'))
    # 密码单存一个表 hash_userInfo
    # r.hset('hash_userInfo', patientid, patient.get('password'))
    print 'redisSavePatient done'
    return '200200'  # 数据写入成功


# 储存医生资料到redis中
def redisSaveDoctor(redis_connect, doctor):
    r = redis_connect
    doctorid = "hash_doctor_%s" % doctor.get('tel')
    r.hset(doctorid, 'tel', doctor.get('tel'))
    r.hset(doctorid, 'age', doctor.get('age'))
    r.hset(doctorid, 'pic', doctor.get('pic'))
    r.hset(doctorid, 'name', doctor.get('name'))
    r.hset(doctorid, 'gender', doctor.get('gender'))
    r.hset(doctorid, 'colliction_count', doctor.get('colliction_count'))
    r.hset(doctorid, 'ndividual_resume', doctor.get('ndividual_resume'))
    r.hset(doctorid, 'adept', doctor.get('adept'))
    r.hset(doctorid, 'comment_count', doctor.get('comment_count'))
    r.hset(doctorid, 'grade', doctor.get('grade'))
    r.hset(doctorid, 'treatment_count', doctor.get('treatment_count'))
    r.hset(doctorid, 'qualification_pic', doctor.get('qualification_pic'))
    r.hset(doctorid, 'identification_pic', doctor.get('identification_pic'))
    r.hset(doctorid, 'hospital', doctor.get('hospital'))
    r.hset(doctorid, 'current_task_count', doctor.get('current_task_count'))
    # 密码单存一个表 hash_userInfo
    # r.hset('hash_userInfo', doctorid, doctor.get('password'))
    print 'redisSaveDoctor done'
    return '200200'


# 查询redis 中存在病人或医生的密码
def redisQueryPatientOrDoctorPWD(redis_connect, tel, userType):
    if userType == 'doctor':
        r = redis_connect.hget('hash_userInfo', 'hash_doctor_%s' % tel)
    elif userType == 'patient':
        r = redis_connect.hget('hash_userInfo', 'hash_patient_%s' % tel)
    else:
        return False
    return r


# 判断病人或医生是否已经注册
def isExistsPatientOrDoctor(redis_connect, tel, userType):
    if userType == 'doctor':
        r = redis_connect.exists('hash_doctor_%s' % tel)
    elif userType == 'patient':
        r = redis_connect.exists('hash_patient_%s' % tel)
    else:
        return '200201'
    return r


if __name__ == "__main__":
    redis_connect = connect('192.168.1.18')
