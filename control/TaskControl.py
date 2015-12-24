# coding:utf8
import uuid
import json
import dao.RedisDAO

rc = dao.RedisDAO.connect('192.168.1.18')


def addTask(redis_connect, detailTask):
    if not redis_connect.exists(detailTask.get('id')):
        detailTask['id'] = uuid.uuid1()
        redis_connect.hmset(detailTask.get('id'), detailTask)
    j = json.dumps(detailTask)
    return redis_connect.publish('handinhand',j)


if __name__ == '__main__':
    dc = {}
    dc["id"]="aaaaaaaaaa"
    dc["symptom"]=u"头痛"
    dc["type"]="self"

    print addTask(rc,dc)

