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
    key = 'channel_hash_detailTask_%s*' % detailTask.get('patient_tel')
    if redis_connect.keys(key):
        return '200303'  # 同一个人同时只能发布一个任务
    if not redis_connect.exists(detailTask.get('id')):
        # 生成详细任务ID
        detailTask['id'] = 'channel_hash_detailTask_%s_%s' % (detailTask.get('patient_tel'), int(time.time()))
        # 1.向channel_hash_detailTask任务列表中添加该任务
        redis_connect.hmset(detailTask.get('id'), detailTask)
        # 2.将任务通过接口url给TCP服务器
        pushTask(redis_connect, 'addTask')

        return '10002 , detailTaskID=%s' % detailTask['id']  # 发布任务成功,并返回任务ID
    else:
        return '200301'  # 同一人同时间重复提交任务


# 删除当前任务
def delectTask(redis_connect, detailTask):
    print 'current id = ', detailTask.get('id')
    r = redis_connect.delete(detailTask.get('id'))
    if r == 1:
        return '10009'  # 删除成功
    else:
        return '200306'  # 删除异常


# 更新任务信息
def editTask(redis_connect, detailTask):
    ttltime = redis_connect.ttl(detailTask.get('id'))
    if ttltime == -1:
        redis_connect.hmset(detailTask.get('id'), detailTask)
        return '10006'  # 任务跟新成功
    else:
        return '200304'  # 当前任务已经有人接受，无法修改


# 判断该用户当前是否有发布的任务
def queryTask(redis_connect, patient_tel):
    key = 'channel_hash_detailTask_%s*' % patient_tel
    task = redis_connect.keys(key)
    if task:

        expirationTime = redis_connect.ttl(task[0])
        taskentity = redis_connect.hgetall(task[0])
        rdict = {}
        rdict['expirationTime'] = str(expirationTime)
        rdict['task'] = taskentity
        return json.dumps(rdict)
    else:
        return '10004'  # 当前没有发布任何任务，可以发布新任务。


# 根据任务ID 查询 当前任务有多少医生接受
def queryTaskDoctorsById(redis_connect, detailTaskID):
    print 'queryTaskDoctorsById id=', detailTaskID
    r = redis_connect.lrange('list_%s_doctors' % detailTaskID, 0, -1)
    doctors = []
    for i in r:
        doctor = redis_connect.hgetall(i)
        doctor.pop('current_task_count')
        doctor.pop('password')
        doctors.append(doctor)
    if doctors:
        return json.dumps(doctors)
    else:
        return '200309'  # 当前暂时无医生响应任务


# 通过url接口打任务 给TCP服务器，
# @what 事件类型 'addTask' , 'addTask' , 'acceptDoctor' , 'unacceptDoctor'
# @doctor_tel 医生电话
# @patient_tel 病人电话
def pushTask(redis_connect, what, doctor_tel=None, patient_tel=None, ip='192.168.1.124', port=9080):
    url = 'http://%s:%d/' % (ip, port)
    # 当执行添加任务时（要推送的数据是 任务详细本身 给所有在线医生）
    if what == 'addTask':
        data = queryAllTask(redis_connect)
        values = {'what': what, 'data': data}
    # 医生接受任务 （要推送的数据是 接受任务的所有医生 给病人）
    elif what == 'acceptTask':
        if doctor_tel == None or patient_tel == None:
            return '200402'  # 必须传递医生和病人电话号码
        doctors = []
        for d in doctor_tel:
            doctors.append(redis_connect.hgetall(d))
        print 'acceptTask patient_tel+ data = ', patient_tel, json.dumps(doctors)
        values = {'what': what, 'tel': patient_tel, 'data': 30001}  # 医生响应您的任务
    # 病人接受医生 TODO（要推送的数据是 1，给被选中的医生回复成功。2，给未被选中的医生回复未被选中由服务器来做）
    elif what == 'acceptDoctor':
        if doctor_tel == None:
            return '200402'  # 必须传递医生和病人电话号码
        values = {'what': what, 'tel': doctor_tel, 'data': 30002}  # 病人选择了您为他治疗
    elif what == 'unacceptDoctor':
        if doctor_tel == None:
            return '200402'  # 必须传递医生和病人电话号码
        values = {'what': what, 'tel': doctor_tel, 'data': 230001}  # 病人放弃了您对他的治疗
    elif what == 'deleteAcceptedDoctor':
        if doctor_tel == None:
            return '200402'  # 必须传递医生和病人电话号码
        values = {'what': what, 'tel': doctor_tel, 'data': 230001}  # 病人放弃了您对他的治疗
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
    list_doctors = redis_connect.lrange('list_channel_%s_doctors' % detailTask.get('id'), 0, -1)
    doctor_count = len(list_doctors)

    # 1.判断当前任务医生数量
    if doctor_count == 0:
        # 2.如果是第一次被接受则在任务集合中保存并设立过期时间
        print 'acceptTask current detailTaskID = ', detailTask.get('id')
        r = pipeline.expire(detailTask.get('id'), int(detailTask.get('task_timeout')))
        print 'acceptTask current expire = ', r
    elif doctor_count >= 3:
        return '200302'  # 当前任务接受者以满

    # 判断医生当前已接受任务列表
    rtask = redis_connect.hget('hash_doctor_%s' % doctor_tel, 'current_task_count')
    if rtask == None:
        task_list = []
    else:
        task_list = json.loads(rtask)
    if detailTask.get(id) in task_list:
        return '200310' # 请勿重复接受
    current_doctor_tasks = len(task_list)
    print 'def acceptTask tasks = ', current_doctor_tasks
    if int(current_doctor_tasks) < 5:
        # 3.医生当前已接受任务追加在医生任务列表中
        task_list.append(detailTask.get('id'))
        # 医生的信息中更新任务列表
        redis_connect.hset('hash_doctor_%s' % doctor_tel, 'current_task_count', json.dumps(task_list))
    else:
        return '200305'  # 当前医生可接受任务数量已满

    # 4.当前任务医生数+1
    doctor_count = doctor_count + 1
    pipeline.hset(detailTask.get('id'), 'doctor_count', doctor_count)
    # 5.将医生添加到该任务的响应医生列表中
    for i in list_doctors:
        if i == 'hash_doctor_%s' % doctor_tel:
            return '200307'  # 该医生已经接单
    # 将医生ID信息保存在 list_channel_hash_detailTask_ 这个列表中
    redis_connect.lpush('list_%s_doctors' % detailTask.get('id'), 'hash_doctor_%s' % doctor_tel)
    # 设置过期时间 和 频道任务时间相同
    redis_connect.expire('list_%s_doctors' % detailTask.get('id'), int(detailTask.get('task_timeout')))
    # 6.通知发任务的病人，有医生接单
    list_doctors = redis_connect.lrange('list_%s_doctors' % detailTask.get('id'), 0, -1)
    print 'befor send list_doctors = ', list_doctors
    pushTask(redis_connect, 'acceptTask', list_doctors, detailTask.get('patient_tel'))

    pipeline.execute()  # 事务执行
    return '10008'  # 接受任务成功


# 病人根据接单医生，选择为他治疗的医生
# @redis_connect  连接Redis操作实体
# @detailTask 任务实体，字典格式(必须具备id，task_timeout默认30分)
# @doctor_tel 医生电话
def acceptDoctor(redis_connect, detailTask, doctor_tel):
    # 1,在详细任务记录中当前任务
    task = redis_connect.hgetall(detailTask.get('id'))
    redis_connect.hmset(detailTask.get('id')[8:], task)
    # 2.通知被接受医生，病人已经选择了他
    # 2.1 在线情况
    pushTask(redis_connect, what='acceptDoctor', doctor_tel=doctor_tel)

    # 3.通知未被接受的医生，病人未选择他们
    list_doctors = redis_connect.lrange('list_%s_doctors' % detailTask.get('id'), 0, -1)
    doctor_tels = [i[12:] for i in list_doctors]
    doctor_tels.remove(doctor_tel)
    for tel in doctor_tels:
        pushTask(redis_connect, what='unacceptDoctor', doctor_tel=tel)
    # 5.删除该任务的响应医生列表
    redis_connect.delete('list_%s_doctors' % detailTask.get('id'))
    # 6.结束在频道任务集合中该任务的声明周期
    redis_connect.expire(detailTask.get('id'), int(1))
    return '10005'  # 接受医生成功


# 病人删除接受任务医生
def deleteAcceptedDoctor(redis_connect, detailTask, doctor_tel):
    # 1.从该任务的响应医生列表中，删除当前医生
    r = redis_connect.lrem('list_%s_doctors' % detailTask.get('id'), 1, 'hash_doctor_%s' % doctor_tel)
    if r != 1:
        return '200308'  # 删除当前响应医生异常
    # 2.通知当前医生，病人放弃了您对他的治疗
    r = pushTask(redis_connect, 'deleteAcceptedDoctor', doctor_tel)
    if r != '10001':
        return '200401'  # 推送异常
    # 3.当前医生的任务列表删除该任务
    task_list = json.loads(redis_connect.hget('hash_doctor_%s' % doctor_tel, 'current_task_count'))
    task_list.remove(detailTask.get('id'))
    redis_connect.hset('hash_doctor_%s' % doctor_tel, 'current_task_count', json.dumps(task_list))
    # 4.将当前医生加入该任务的黑名单
    blacklist = []
    blacklist.append('hash_doctor_%s' % doctor_tel)
    redis_connect.hset(detailTask.get('id'), 'blacklist', json.dumps(blacklist))
    return '' # 删除响应医生成功


# 查询所有任务
def queryAllTask(redis_connect):
    return RedisDAO.queryChannelTask(redis_connect)

# 根据医生电话， 查询以接任务
def queryAcceptTaskByTel(redis_connect,tel):
    r = redis_connect.keys('hash_doctor_%s'%tel)
    current_task_count = r.get('current_task_count')
    if current_task_count:
        return current_task_count
    else:
        return '200311' # 暂时未接去任何任务

def queryDoctorByTel(redis_connect, tel):
    return RedisDAO.queryDoctorByTel(redis_connect, tel)


if __name__ == '__main__':
    rc = RedisDAO.connect('192.168.1.18')
    pushTask(rc)
    rc.delete()

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
