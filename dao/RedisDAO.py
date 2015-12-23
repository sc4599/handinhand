# coding:utf8
import redis
from entity.Entity import DetailTask
from util.Util import Config

globalsR = None


def connect(host=None, post=6379, db=0, password='songchao'):
    print(u'准备连接redis。。。IP = %s' % host)
    redis_connect = redis.StrictRedis(host=host, port=post, db=db, password='songchao')
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
    taskid = "taks:%s" % detailTask['id']
    r.hsetnx(taskid, 'id', detailTask['id'])
    r.hsetnx(taskid, 'symptom', detailTask['symptom'])
    r.hsetnx(taskid, 'datetime', detailTask['datetime'])
    r.hsetnx(taskid, 'lat', detailTask['lat'])
    r.hsetnx(taskid, 'lon', detailTask['lon'])
    r.hsetnx(taskid, 'patient_tel', detailTask['patient_tel'])
    r.hsetnx(taskid, 'patient_name', detailTask['patient_name'])
    r.hsetnx(taskid, 'doctor_tel', detailTask['doctor_tel'])
    r.hsetnx(taskid, 'doctor_name', detailTask['doctor_name'])
    print u'储存完毕'

# 储存病人资料到redis中
def redisSavePatient(redis_connect, patient):
    r = redis_connect
    patientid = "patient:%s" % patient['tel']
    r.hsetnx(patientid, 'tel', patient['tel'])
    r.hsetnx(patientid, 'pic', patient['pic'])
    r.hsetnx(patientid, 'name', patient['name'])
    r.hsetnx(patientid, 'gender', patient['gender'])
    r.hsetnx(patientid, 'age', patient['age'])
    r.hsetnx(patientid, 'treatment_count', patient['treatment_count'])
    r.hsetnx(patientid, 'colliction_list_id', patient['colliction_list_id'])
    print 'done'

# 储存医生资料到redis中
def redisSaveDoctor(redis_connect, doctor):
    r = redis_connect
    doctorid = "doctor:%s" % doctor['tel']
    r.hsetnx(doctorid, 'tel', doctor['tel'])
    r.hsetnx(doctorid, 'age', doctor['age'])
    r.hsetnx(doctorid, 'pic', doctor['pic'])
    r.hsetnx(doctorid, 'name', doctor['name'])
    r.hsetnx(doctorid, 'gender', doctor['gender'])
    r.hsetnx(doctorid, 'colliction_count', doctor['colliction_count'])
    r.hsetnx(doctorid, 'treatment_count', doctor['treatment_count'])
    r.hsetnx(doctorid, 'qualification_pic', doctor['qualification_pic'])
    r.hsetnx(doctorid, 'identification_pic', doctor['identification_pic'])
    r.hsetnx(doctorid, 'hospital', doctor['hospital'])
    print 'done'



def publishTask(redis_connect, detailTask):
    return redis_connect.publish('tasks', str(detailTask))


if __name__ == "__main__":
    c = Config()
    ip = c.reidsIP
    psw = c.redisAUTH
    redis_connect = connect(host=ip, password=psw)
    # print redis_connect.get('name')
    print redis_connect.exists('taskdfs')
