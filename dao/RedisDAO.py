# coding:utf8
import uuid
import redis
from entity.Entity import DetailTask
from util.Util import Config

globalsR = None


def connect(redisIP=None, post=6379, db=0, password='songchao'):
    print(u'准备连接redis。。。IP = %s' % redisIP)
    redis_connect = redis.StrictRedis(host=redisIP, port=post, db=db, password='songchao', charset='utf-8',
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


# 储存病人资料到redis中
def redisSavePatient(redis_connect, patient):
    r = redis_connect
    patientid = "hash_patient_%s" % patient.get('tel')
    r.hset(patientid, 'tel', patient.get('tel'))
    r.hset(patientid, 'password', patient.get('password'))
    r.hset(patientid, 'pic', patient.get('pic'))
    r.hset(patientid, 'name', patient.get('name'))
    r.hset(patientid, 'gender', patient.get('gender'))
    r.hset(patientid, 'age', patient.get('age'))
    r.hset(patientid, 'treatment_count', patient.get('treatment_count'))
    r.hset(patientid, 'colliction_list_id', patient.get('colliction_list_id'))
    print 'redisSavePatient done'
    return '200200'  # 数据写入成功


# 储存医生资料到redis中
def redisSaveDoctor(redis_connect, doctor):
    r = redis_connect
    doctorid = "hash_doctor_%s" % doctor.get('tel')
    r.hset(doctorid, 'tel', doctor.get('tel'))
    r.hset(doctorid, 'password', doctor.get('password'))
    r.hset(doctorid, 'age', doctor.get('age'))
    r.hset(doctorid, 'pic', doctor.get('pic'))
    r.hset(doctorid, 'name', doctor.get('name'))
    r.hset(doctorid, 'gender', doctor.get('gender'))
    r.hset(doctorid, 'ndividual_resume', doctor.get('ndividual_resume'))
    r.hset(doctorid, 'adept', doctor.get('adept'))
    r.hset(doctorid, 'colliction_count', doctor.get('colliction_count'))
    r.hset(doctorid, 'treatment_count', doctor.get('treatment_count'))
    r.hset(doctorid, 'qualification_pic', doctor.get('qualification_pic'))
    r.hset(doctorid, 'identification_pic', doctor.get('identification_pic'))
    r.hset(doctorid, 'hospital', doctor.get('hospital'))
    print 'redisSaveDoctor done'


# 查询redis 中存在病人
def redisQueryPatient(redis_connect, tel):
    r = redis_connect.get('hash_patient_%s' % tel)
    print r


# 查询redis 中存在医生
def redisQueryDoctor(redis_connect, tel):
    r = redis_connect.get('hash_doctor_%s' % tel)
    print r


# 判断病人是否已经注册
def isExistsPatient(redis_connect, tel):
    r = redis_connect.exists('hash_patient_%s' % tel)
    return r


def publishTask(redis_connect, detailTask):
    return redis_connect.publish('tasks', str(detailTask) if (isinstance(detailTask, str)) else detailTask)


if __name__ == "__main__":
    c = Config()
    ip = c.reidsIP
    psw = c.redisAUTH
    redis_connect = connect(redisIP=ip, password=psw)
    # redis_connect.set('s1','test', ex=30)
    # r = redis_connect.keys('t*')
    import time

    print int(time.time())
