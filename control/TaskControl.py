# coding:utf8
import uuid
import json, time
from dao import RedisDAO
import urllib2, urllib


# rc = RedisDAO.connect('192.168.1.18')


# @redis_connect  连接Redis操作实体
# @detailTask  任务实体，字典格式
# return 返回当前频道接受到任务的人数
def addTask(redis_connect, detailTask):
    key = 'channel_hash_detailTask_' + detailTask.get('tel') + '*'
    if redis_connect.keys(key):
        return '200303'  # 同一个人同时只能发布一个任务
    if not redis_connect.exists(detailTask.get('id')):
        # 生成详细任务ID
        detailTask['id'] = 'hash_detailTask_%s_%s' % (detailTask.get('patient_tel'), int(time.time()))
        # 1.向channel_hash_detailTask任务列表中添加该任务
        redis_connect.hmset('channel_%s' % detailTask.get('id'), detailTask)
        # 2.将任务通过接口url给TCP服务器
        pushTask(redis_connect)

        return '10002'  # 发布任务成功
    else:
        return '200301'  # 同一人同时间重复提交任务


# 通过url接口打任务 给TCP服务器，
# @what 事件类型
# @doctor_tel 医生电话
# @patient_tel 病人电话
def pushTask(redis_connect,what,doctor_tel=None,patient_tel=None):
    url = 'http://192.168.1.124:9080/'
    if what == 'addTask':
        data = queryAllTask(redis_connect)
        values = {'what': what,'data':data}
    elif what == 'acceptTask':
        if doctor_tel == None or patient_tel==None:
            return '200402' #  必须传递医生和病人电话号码
        data = queryDoctorByTel(redis_connect,doctor_tel)
        values = {'what': what,'tel':doctor_tel,'data':data}
    elif what == 'acceptDoctor':
        if doctor_tel == None or patient_tel==None:
            return '200402' #  必须传递医生和病人电话号码
        # data =
    post_data = urllib.urlencode(values)
    req = urllib2.Request(url, data=post_data)
    response = urllib2.urlopen(req)
    res = response.read()
    if res == '...succeed...':
        return '10001'  # 推送任务成功
    else:
        return '200401'  # 与tcp服务器连接异常


# 接受任务处理函数
# @redis_connect  连接Redis操作实体
# @detailTask 任务实体，字典格式(必须具备id，task_timeout默认30分)
# @doctor_tel 医生电话
def acceptTask(redis_connect, detailTask, doctor_tel):
    pipeline = redis_connect.pipeline()
    doctor_count = len(redis_connect.llen('list_%s_doctors' % detailTask.get('id')))

    # 1.判断当前任务医生数量
    if doctor_count == 0:
        # 2.如果是第一次被接受则在任务集合中保存并设立过期时间
        pipeline.expire('channel_%s' % detailTask.get('id'), int(detailTask.get('task_timeout')))
    elif doctor_count >= 3:
        return '200302'  # 当前任务接受者以满

    # 判断医生当前已接受任务数量
    current_doctor_tasks = redis_connect.hget('hash_doctor_%s' % doctor_tel, 'current_task_count')
    if current_doctor_tasks < 5:
        # 3.医生当前已接受任务数量+1
        current_doctor_tasks = current_doctor_tasks + 1
        redis_connect.hset('hash_doctor_%s' % doctor_tel, 'current_task_count', current_doctor_tasks)
    else:
        return '200304'  # 当前医生可接受任务数量已满

    # 4.当前任务医生数+1
    doctor_count = doctor_count + 1
    pipeline.hset(detailTask.get('id'), 'doctor_count', doctor_count)
    # 5.将医生添加到该任务的响应医生列表中
    pipeline.lpush('list_%s_doctors' % detailTask.get('id'))
    # 6.通知发任务的病人，有医生接单

    pipeline.execute()  # 事务执行


# 病人根据接单医生，选择为他治疗的医生
def acceptDoctor(redis_connect, detailTask, doctor, patient):
    # 1,更新任务里列表中该任务的病人牵手时间
    redis_connect.hset(detailTask.get('id'), 'accept_time', int(time.time()))
    # 2.通知被接受医生，病人已经选择了他

    pass


# 查询所有任务
def queryAllTask(redis_connect):
    return RedisDAO.queryChannelTask(redis_connect)

def queryDoctorByTel(redis_connect,tel):
    return RedisDAO.queryDoctorByTel(redis_connect,tel)

if __name__ == '__main__':
    rc = RedisDAO.connect('192.168.1.18')
    pushTask(rc)
    # l.append('hash_detailTask_13887083253_14224545')
    # l.append('hash_detailTask_13887083253_14226546')
    # l.append('hash_detailTask_13887083257_14225547')
    # print rc.lpush('list_handinhand_current_task',l)
    # rc.lpush('list_handinhand_current_task','hash_detailTask_13887083253_14224545')
    # rc.lpush('list_handinhand_current_task','hash_detailTask_13887083253_14226546')
    # rc.lpush('list_handinhand_current_task','hash_detailTask_13887083257_14225547')
    # llen = rc.llen('list_handinhand_current_task')
    #
    # for i in range(llen):
    #     key = rc.lindex('list_handinhand_current_task', i)
    #     l.append(rc.hgetall(key))
    #
    # print json.dumps(l)
    # print rc.lrem('list_handinhand_current_task', 0, 'hash_detailTask_13887083253_14224545')
    # print len(rc.keys('t*'))
