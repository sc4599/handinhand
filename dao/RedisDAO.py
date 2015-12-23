# coding:utf8
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
    taskid = "taks:%s" % detailTask.get('id')
    r.hsetnx(taskid, 'id', detailTask.get('id'))
    r.hsetnx(taskid, 'symptom', detailTask.get('symptom'))
    r.hsetnx(taskid, 'datetime', detailTask.get('datetime'))
    r.hsetnx(taskid, 'lat', detailTask.get('lat'))
    r.hsetnx(taskid, 'lon', detailTask.get('lon'))
    r.hsetnx(taskid, 'patient_tel', detailTask.get('patient_tel'))
    r.hsetnx(taskid, 'patient_name', detailTask.get('patient_name'))
    r.hsetnx(taskid, 'doctor_tel', detailTask.get('doctor_tel'))
    r.hsetnx(taskid, 'doctor_name', detailTask.get('doctor_name'))
    print u'储存完毕'


# 储存病人资料到redis中
def redisSavePatient(redis_connect, patient):
    r = redis_connect
    patientid = "patient_%s" % patient.get('tel')
    r.hset(patientid, 'tel', patient.get('tel'))
    r.hset(patientid, 'pic', patient.get('pic'))
    r.hset(patientid, 'name', patient.get('name'))
    r.hset(patientid, 'gender', patient.get('gender'))
    r.hset(patientid, 'age', patient.get('age'))
    r.hset(patientid, 'treatment_count', patient.get('treatment_count'))
    r.hset(patientid, 'colliction_list_id', patient.get('colliction_list_id'))
    print 'done'
    return '200102' # 注册成功


# 储存医生资料到redis中
def redisSaveDoctor(redis_connect, doctor):
    r = redis_connect
    doctorid = "doctor_%s" % doctor.get('tel')
    r.hset(doctorid, 'tel', doctor.get('tel'))
    r.hset(doctorid, 'age', doctor.get('age'))
    r.hset(doctorid, 'pic', doctor.get('pic'))
    r.hset(doctorid, 'name', doctor.get('name'))
    r.hset(doctorid, 'gender', doctor.get('gender'))
    r.hset(doctorid, 'colliction_count', doctor.get('colliction_count'))
    r.hset(doctorid, 'treatment_count', doctor.get('treatment_count'))
    r.hset(doctorid, 'qualification_pic', doctor.get('qualification_pic'))
    r.hset(doctorid, 'identification_pic', doctor.get('identification_pic'))
    r.hset(doctorid, 'hospital', doctor.get('hospital'))
    print 'done'


# 查询redis 中存在病人
def redisQueryPatient(redis_connect, tel):
    r = redis_connect.get('patient_%s' % tel)
    print r


# 查询redis 中存在医生
def redisQueryDoctor(redis_connect, tel):
    r = redis_connect.get('doctor_%s' % tel)
    print r

# 判断病人是否已经注册
def isExistsPatient(redis_connect, tel):
    r = redis_connect.exists('patient_%s'%tel)
    return r



def publishTask(redis_connect, detailTask):
    return redis_connect.publish('tasks', str(detailTask) if (isinstance(detailTask, str)) else detailTask)


if __name__ == "__main__":
    c = Config()
    ip = c.reidsIP
    psw = c.redisAUTH
    redis_connect = connect(redisIP=ip, password=psw)
    r = isExistsPatient(redis_connect,'12345678901')
    print r
