# coding:utf8
import uuid
import json, time
from dao import RedisDAO

rc = RedisDAO.connect('192.168.1.18')


# @redis_connect  连接Redis操作实体
# @detailTask  任务实体，字典格式
# return
def addTask(redis_connect, detailTask):
    if not redis_connect.exists(detailTask.get('id')):
        detailTask['id'] = 'detailTask_%s_%s' % (detailTask.get('tel'), int(time.time()))
        redis_connect.hmset(detailTask.get('id'), detailTask) # 向任务详细中添加任务
        redis_connect.hmset('channel_%s'%detailTask.get('id'),detailTask) # 向在线任务通道添加任务
        tasks = []
        tasks.append(detailTask)
        j = json.dumps(tasks)  # 将 字段转换成json
        return redisPublist(redis_connect, j) # 将任务发布到任务频道
    else:
        return '200301'  # 同一人同时间重复提交任务

# 接受任务处理函数
# @redis_connect  连接Redis操作实体
# @detailTask 任务实体，字典格式
def accept(redis_connect, detailTask):
    pipeline = redis_connect.pipeline()
    pipeline.expire('channel_%s'%detailTask.get('id'),3600) # 为在线任务通道任务添加过期时间
    pipeline.hset(detailTask.get('id'),'accept_time',int(time.time()))# 为任务详细中 更新该任务的接受时间
    pipeline.execute()# 事务执行

# @redis_connect  连接Redis操作实体
# @jsonEntity  对应的实体字典转换出来的json
# @channel  发布消息通道 默认是 'handinhand'
# return 接收到这条广播的人数
def redisPublist(redis_connect, jsonEntity, channel='handinhand'):
    return redis_connect.publish(channel, jsonEntity)


if __name__ == '__main__':
    dc = {}
    dc["id"] = "aaaaaaaaaa"
    dc["symptom"] = u"头痛"
    dc["type"] = "self"
    l =[]
    l.append(dc)
    j = json.dumps(l)

    print j
