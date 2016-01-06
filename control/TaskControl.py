# coding:utf8
import uuid
import json, time
from dao import RedisDAO
import urllib2,urllib
# rc = RedisDAO.connect('192.168.1.18')


# @redis_connect  连接Redis操作实体
# @detailTask  任务实体，字典格式
# return 返回当前频道接受到任务的人数
def addTask(redis_connect, detailTask):
    if not redis_connect.exists(detailTask.get('id')):
        # 生成详细任务ID
        detailTask['id'] = 'hash_detailTask_%s_%s' % (detailTask.get('patient_tel'), int(time.time()))
        # 1.向channel_hash_detailTask任务列表中添加该任务
        redis_connect.hmset('channel_%s' % detailTask.get('id'), detailTask)
        # 2.将任务通过接口url给TCP服务器
        pushTask(redis_connect)
        # redis_connect.lpush('list_handinhand_current_task', detailTask.get('id'))
        # # 当前任务列表
        list_handinhand_current_task = []
        # # 先查到list长度， 迭代list中内个key ， 通过key查找对应的 hash， 存入Json，发布到频道中
        # for i in range(redis_connect.llen('list_handinhand_current_task')):
        #     key = redis_connect.lindex('list_handinhand_current_task', i)
        #     list_handinhand_current_task.append(redis_connect.hgetall(key))
        r = redis_connect.keys('channel_*')
        for k in r:
            list_handinhand_current_task.append(redis_connect.hgetall(k))
        j = json.dumps(list_handinhand_current_task)  # 将 字段转换成json
        # print j # 打印当前任务信息
        redisPublist(redis_connect, j)  # 将任务发布到任务频道 返回当前频道接受到任务的人数
        return '10002'# 发布任务成功
    else:
        return '200301'  # 同一人同时间重复提交任务

# def pushTask(redis_connect):
#     r = queryAllTask(redis_connect)
#     print type(r)
#     url = 'http://192.168.1.124:9080/'+r
#     req = urllib2.Request(url)
#     res_data = urllib2.urlopen(req)
#     res = res_data.read()
#     if  res == '...succeed...':
#         return '10001' # 推送任务成功
#     else:
#         return '200401'# 与tcp服务器连接异常

def pushTask(redis_connect):
    r = queryAllTask(redis_connect)
    url = 'http://192.168.1.124:9080/'
    values = {'msg': r}
    post_data = urllib.urlencode(values)
    req = urllib2.Request(url, data=post_data)
    response  = urllib2.urlopen(req)
    res = response.read()
    if  res == '...succeed...':
        return '10001' # 推送任务成功
    else:
        return '200401'# 与tcp服务器连接异常


# 接受任务处理函数
# @redis_connect  连接Redis操作实体
# @detailTask 任务实体，字典格式
# @doctor_tel 医生电话
def accept(redis_connect, detailTask, doctor_tel):
    pipeline = redis_connect.pipeline()
    doctor_count = len(redis_connect.keys('%s*' % detailTask.get('id')))

    # 判断当前医生数量
    if doctor_count == 0:
        pipeline.expire('channel_%s' % detailTask.get('id'), int(detailTask.get('task_timeout')))  # 为在线任务通道任务添加过期时间
        pipeline.execute()  # 事务执行

    elif doctor_count < 3:
        doctor_count = doctor_count + 1
        pipeline.hset(detailTask.get('id'), 'doctor_count', doctor_count)
        # 如果是第一个人接任务， 则给任务设置声明周期。
        pipeline.hset(detailTask.get('id'), 'accept_time', int(time.time()))  # 为任务详细中 更新该任务的接受时间
        pipeline.execute()  # 事务执行
    else:
        return '200302'  # 当前任务接受者以满


# @redis_connect  连接Redis操作实体
# @jsonEntity  对应的实体字典转换出来的json
# @channel  发布消息通道 默认是 'handinhand'
# return 接收到这条广播的人数
def redisPublist(redis_connect, jsonEntity, channel='handinhand'):
    return redis_connect.publish(channel, jsonEntity)

# 查询所有任务
def queryAllTask(redis_connect):
    return RedisDAO.queryChannelTask(redis_connect)

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
