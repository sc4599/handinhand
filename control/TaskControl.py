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
        pushTask( 'addTask')

        return '10002 , detailTaskID=%s' % detailTask['id']  # 发布任务成功,并返回任务ID
    else:
        return '200301'  # 同一人同时间重复提交任务


# 删除当前任务
def delectTask(redis_connect, detailTask):
    print 'this is delectTask id =', detailTask.get('id')
    if redis_connect.exists('list_%s_doctors'%detailTask.get('id')):
        return '200312' # 当前任务已经有医生接单，无法删除
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
    print 'this is queryTaskDoctorsById id=', detailTaskID
    r = redis_connect.lrange('list_%s_doctors' % detailTaskID, 0, -1)
    doctors = []
    for i in r:
        doctor = redis_connect.hgetall(i)
        if 'password' in doctor:
            doctor.pop('password')
        if 'current_task_count' in doctor:
            doctor.pop('current_task_count')
        doctors.append(doctor)
    if doctors:
        return json.dumps(doctors)
    else:
        return '200309'  # 当前暂时无医生响应任务


# 根据任务ID 查询任务详细
def queryTaskInfoById(redis_connect,detailTaskID):
    r = redis_connect.hgetall(detailTaskID)
    return r


# 通过url接口打任务 给TCP服务器，
# @what 事件类型 'addTask' , 'addTask' , 'acceptDoctor' , 'unacceptDoctor'
# @doctor_tel 医生电话
# @patient_tel 病人电话
def pushTask(what, doctor_tel=None, patient_tel=None, channelTaskID=None, name = None,ip='192.168.1.124', port=9080):
    url = 'http://%s:%d/' % (ip, port)
    print 'this is pushTask what = %s ,doctor_tel = %s,patient_tel = %s , channelID = %s'%(what,str(doctor_tel),str(patient_tel),str(channelTaskID))
    # 当执行添加任务时（要推送的数据是 任务详细本身 给所有在线医生）
    if what == 'addTask':
        # data = queryAllTask(redis_connect)
        data = {'resultCode': 30000,
                'msg': {'patient_tel': patient_tel, 'doctor_tel': doctor_tel, 'channelTaskID': channelTaskID ,'name':name}}
        values = {'what': what, 'data': json.dumps(data)}  # 医生们有新任务了
    # 医生接受任务 （要推送的数据是 接受任务的所有医生 给病人）
    elif what == 'acceptTask':
        if doctor_tel == None or patient_tel == None:
            return '200402'  # 必须传递医生和病人电话号码

        data = {'resultCode': 30001,
                'msg': {'patient_tel': patient_tel, 'doctor_tel': doctor_tel, 'channelTaskID': channelTaskID,'name':name}}
        values = {'what': what, 'tel': patient_tel, 'data': json.dumps(data)}  # 医生响应您的任务
    # 病人接受医生 TODO（要推送的数据是 1，给被选中的医生回复成功。2，给未被选中的医生回复未被选中由服务器来做）
    elif what == 'acceptDoctor':
        print 'current  acceptDoctor doctor_tel = %s '%doctor_tel
        if doctor_tel == None :
            return '200402'  # 必须传递医生和病人电话号码
        data = {'resultCode': 30002,
                'msg': {'patient_tel': patient_tel, 'doctor_tel': doctor_tel, 'channelTaskID': channelTaskID,'name':name}}
        values = {'what': what, 'tel': doctor_tel, 'data': json.dumps(data)}  # 病人选择了您为他治疗
    elif what == 'unacceptDoctor':
        if doctor_tel == None:
            return '200402'  # 必须传递医生和病人电话号码
        data = {'resultCode': 30003,
                'msg': {'patient_tel': patient_tel, 'doctor_tel': doctor_tel, 'channelTaskID': channelTaskID,'name':name}}
        values = {'what': what, 'tel': doctor_tel, 'data': json.dumps(data)}  # 病人没有选择您为他的看病
    elif what == 'deleteAcceptedDoctor':
        if doctor_tel == None:
            return '200402'  # 必须传递医生和病人电话号码
        data = {'resultCode': 30004,
                'msg': {'patient_tel': patient_tel, 'doctor_tel': doctor_tel, 'channelTaskID': channelTaskID,'name':name}}
        values = {'what': what, 'tel': doctor_tel, 'data': json.dumps(data)}  # 病人放弃了您对他的治疗
    elif what == 'confirmTask':
        print 'current pushTask confirmTask patient_tel = %s '%patient_tel
        if patient_tel == None:
            return '200402'
        data = {'resultCode': 30005,
                'msg': {'patient_tel': patient_tel, 'doctor_tel': patient_tel, 'channelTaskID': channelTaskID,'name':name}}
        values = {'what': what, 'tel': patient_tel, 'data': json.dumps(data)}  # 医生确定任务成功
        print 'current pushTask content = ',data
    elif what == 'cancelTask':
        if patient_tel == None:
            return '200402'
        data = {'resultCode': 30006,
                'msg': {'patient_tel': patient_tel, 'doctor_tel': doctor_tel, 'channelTaskID': channelTaskID,'name':name}}
        values = {'what': what, 'tel': patient_tel, 'data': json.dumps(data)}  # 医生放弃了对您的治疗
    elif what == 'sendPrivateLetter':
        if doctor_tel == None:
            return '200402'
        data = {'resultCode': 30101,
                'msg': {'patient_tel': patient_tel, 'doctor_tel': doctor_tel, 'channelTaskID': channelTaskID,'name':name}}
        values = {'what': what, 'tel': doctor_tel, 'data': json.dumps(data)}  # 有人给你发了私信
    elif what == 'acceptPrivateLetter':
        if patient_tel == None:
            return '200402'
        data = {'resultCode': 30102,
                'msg': {'patient_tel': patient_tel, 'doctor_tel': doctor_tel, 'channelTaskID': channelTaskID,'name':name}}
        values = {'what': what, 'tel': patient_tel, 'data': json.dumps(data)}  # 医生接受私信
    elif what == 'confirmPrivateLetter':
        if patient_tel == None:
            return '200402'
        data = {'resultCode': 30103,
                'msg': {'patient_tel': patient_tel, 'doctor_tel': doctor_tel, 'channelTaskID': channelTaskID,'name':name}}
        values = {'what': what, 'tel': patient_tel, 'data': json.dumps(data)}  # 通知病人，医生最终接受了你的私信
    elif what == 'cancelTaskPrivateLetter':
        if patient_tel == None:
            return '200402'
        data = {'resultCode': 30104,
                'msg': {'patient_tel': patient_tel, 'doctor_tel': doctor_tel, 'channelTaskID': channelTaskID,'name':name}}
        values = {'what': what, 'tel': patient_tel, 'data': json.dumps(data)}  # 通知病人，医生最取消了你的私信
    post_data = urllib.urlencode(values)
    req = urllib2.Request(url, data=post_data)
    print 'current pushTask req =',req
    response = urllib2.urlopen(req)
    res = response.read()
    print 'pushTask res = ', res
    return '10001'


# 设置过期执行


# 接受任务处理函数
# @redis_connect  连接Redis操作实体
# @detailTask 任务实体，字典格式(必须具备id，task_timeout默认30分)
# @doctor_tel 医生电话
def acceptTask(redis_connect, detailTask, doctor_tel, ):
    # 0 判断任务黑名单是否有自己
    rbl= redis_connect.hget(detailTask.get('id'),'blacklist')
    if rbl == 'None' or rbl == None:
        blacklist = []
    else:
        blacklist = json.loads(rbl)
    if 'hash_doctor_%s'%doctor_tel in blacklist:
        return '200313' # 你当前处于任务黑名单内

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

    # 判断医生当是否接受过当前任务列表
    rtask = redis_connect.hget('hash_doctor_%s' % doctor_tel, 'current_task_count')
    # print u'判断医生当前已接受任务列表 rtask',rtask
    # print u'判断医生当前已接受任务列表 rtask == None',rtask == None
    if rtask == 'None' or rtask == None:
        task_list = []
    else:
        task_list = json.loads(rtask)
    if detailTask.get('id') in task_list:
        return '200310'  # 请勿重复接受
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
    # doctor_count = doctor_count + 1
    # pipeline.hset(detailTask.get('id'), 'doctor_count', doctor_count)
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
    pushTask( 'acceptTask', list_doctors, detailTask.get('patient_tel'), detailTask.get('id'))

    pipeline.execute()  # 事务执行
    return '10008'  # 接受任务成功


# 暂停当前任务过期时间
def pauseTaskTime(redis_connect,detailTaskID):
    surplusTime = redis_connect.ttl(detailTaskID)
    redis_connect.hset(detailTaskID,'task_timeout',surplusTime)
    return '10015' # 任务过期时间暂停成功

# 恢复当前任务过期时间
def resumeTaskTime(redis_connect,detailTaskID):
    surplusTime = redis_connect.hget(detailTaskID,'task_timeout')
    redis_connect.expire(detailTaskID,int(surplusTime))
    return '10016' # 恢复任务过期时间成功

# 病人根据接单医生，选择为他治疗的医生
# @redis_connect  连接Redis操作实体
# @detailTask 任务实体，字典格式(必须具备id，task_timeout默认30分)
# @doctor_tel 医生电话
def acceptDoctor(redis_connect, detailTask, doctor_tel):
    print 'this is acceptDoctor doctor_tel%s'%doctor_tel
    # 1,在当前频道任务中记录当前医生电话
    redis_connect.hset(detailTask.get('id'), 'doctor_tel', doctor_tel)
    # 2.通知被接受医生，病人已经选择了他
    # 2.1 在线情况
    r = pushTask( what='acceptDoctor', doctor_tel=doctor_tel, channelTaskID=detailTask.get('id'))
    print 'this is acceptDoctor r=%s'%r
    print 'this is acceptDoctor id=%s'%detailTask.get('id')
    return '10005'  # 接受医生成功


# 病人删除接受任务医生
def deleteAcceptedDoctor(redis_connect, detailTask, doctor_tel):
    # 1.从该任务的响应医生列表中，删除当前医生
    pip = redis_connect.pipeline()
    r = pip.lrem('list_%s_doctors' % detailTask.get('id'), 1, 'hash_doctor_%s' % doctor_tel)
    # if r != 1:
    #     return '200308'  # 医生已经被删除请勿重复提交
    # 2.通知当前医生，病人放弃了您对他的治疗
    r = pushTask( 'deleteAcceptedDoctor', doctor_tel, channelTaskID=detailTask.get('id'),name=detailTask.get('patient_name'))
    print 'deleteAcceptedDoctor pushTask r =', r
    if r != '10001':
        return '200401'  # 推送异常
    # 3.当前医生的任务列表删除该任务
    task_list = json.loads(redis_connect.hget('hash_doctor_%s' % doctor_tel, 'current_task_count'))
    if detailTask.get('id') in task_list:
        task_list.remove(detailTask.get('id'))
    pip.hset('hash_doctor_%s' % doctor_tel, 'current_task_count', json.dumps(task_list))
    # 4.将当前医生加入该任务的黑名单
    blacklist = []
    blacklist.append('hash_doctor_%s' % doctor_tel)
    pip.hset(detailTask.get('id'), 'blacklist', json.dumps(blacklist))
    pip.execute()
    return '10011'  # 删除响应医生成功


# 医生确定为病人治疗
def confirmTask(redis_connect, detailTask):
    print 'this is confirmTask detailTaskID = ',detailTask.get('id')
    pip = redis_connect.pipeline()
    # 1,生成详细任务记录并在当前任务里添加医生电话号码
    task = redis_connect.hgetall(detailTask.get('id'))
    detailTaskID = detailTask.get('id')[8:]
    pip.hmset(detailTaskID, task)
    # 2.医生行医记录里添加详细任务id（Treatment_count）
    r = redis_connect.hget('hash_doctor_%s'%detailTask.get('doctor_tel'),'treatment_count')
    if r =='None' or r == None:
        treatments = []
    else:
        treatments = json.loads(r)
    treatments.append(detailTaskID)
    pip.hset('hash_doctor_%s' % detailTask.get('doctor_tel'), 'treatment_count', json.dumps(treatments))
    # 3.病人就医记录里添加详细任务id（medical_history）
    r = redis_connect.hget('hash_patient_%s'%detailTask.get('patient_tel'),'medical_history')
    if r =='None' or r == None:
        medicalHistorys = []
    else:
        medicalHistorys  = json.loads(r)
    medicalHistorys.append(detailTaskID)
    pip.hset('hash_patient_%s' % detailTask.get('patient_tel'), 'medical_history', json.dumps(medicalHistorys))
    # 4.通知病人，医生接受了你的任务
    print 'currnet confirmTask patient_tel =',detailTask.get('patient_tel')
    r = pushTask( what='confirmTask',patient_tel=detailTask.get('patient_tel'),
             channelTaskID=detailTask.get('id'))
    print 'currnet confirmTask pushTask r=',r
    if r != '10001':
        return r
    # 5.通知未被接受的医生，病人未选择他们
    print 'current id = ','list_%s_doctors' % detailTask.get('id')
    doctors = redis_connect.lrange('list_%s_doctors' % detailTask.get('id'),0,-1)
    if 'hash_doctor_%s' % detailTask.get('doctor_tel') in doctors:
        doctors.remove('hash_doctor_%s' % detailTask.get('doctor_tel'))
    for i in doctors:
        doctor_tel = i[12:]
        pushTask( what='unacceptDoctor', doctor_tel=doctor_tel, channelTaskID=detailTask.get('id'))
    # 6.结束在频道任务集合中该频道任务的生命周期
    pip.expire(detailTask.get('id'), 1)
    # 7.同时删除医生任务列表中的该条任务！（current_task_count）
    rtasks = redis_connect.hget('hash_doctor_%s' % detailTask.get('doctor_tel'), 'current_task_count')
    tasklist = json.loads(rtasks)
    if detailTask.get('id') in tasklist:
        tasklist.remove(detailTask.get('id'))
    pip.hset('hash_doctor_%s' % detailTask.get('doctor_tel'), 'current_task_count', json.dumps(tasklist))
    # 8.删除该频道任务的响应医生列表（list_*_doctors）
    pip.expire('list_%s_doctors' % detailTask.get('id'),1)
    pip.execute()
    return '10013'  # 确定任务成功


# 医生取消为病人治疗
def cancelTask(redis_connect, detailTask):
    # 1,在当前频道任务中删除当前医生电话
    r = redis_connect.hset(detailTask.get('id'), 'doctor_tel', '00000000000')
    if r !=1 :
        return '' # 通过 id 更改医生电话失败
    # 2.通知病人，医生取消了对你的治疗
    r = pushTask( what='cancelTask', patient_tel=detailTask.get('patient_tel'),
             channelTaskID=detailTask.get('id'))
    if r != '10001':
        return r
    return '10014'  # 取消任务完毕


# 查询所有任务
def queryAllTask(redis_connect):
    return RedisDAO.queryChannelTask(redis_connect)


# 根据医生电话， 查询以接任务
def queryAcceptTaskByTel(redis_connect, tel):
    r = redis_connect.hgetall('hash_doctor_%s' % tel)
    current_task_count = r.get('current_task_count')
    if current_task_count:
        return current_task_count
    else:
        return '200311'  # 暂时未接去任何任务


def queryDoctorByTel(redis_connect, tel):
    return RedisDAO.queryDoctorByTel(redis_connect, tel)


# 病人就医记录
def queryPatientTaskHistory(redis_connect, patient_tel):
    pattern = 'hash_detailTask_%s' % patient_tel
    list = redis_connect.keys(pattern)
    tasks = []
    for i in list:
        entity = redis_connect.hgetall(i)
        tasks.append(entity)
    print tasks


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
