# coding:utf8
import  json

def ab():
    print '11111'

import dao.RedisDAO
rc = dao.RedisDAO.connect('192.168.1.18')
#
# d = {'a':2}
#
# l  = ['private_hash_detailTask_13887083253','private_hash_detailTask_13887083254','private_hash_detailTask_13887083255']
#
# l2 = [i[-11:] for  i in l]
# rc.exists()
# r = rc.keys('channel*')
# d  = {'a':1}
# print json.dumps(l)
# r = rc.hget('hash_doctor_18818684122','current_task_count')
# print json.loads(r)
# print type(json.loads(r))
# print type(r)

# rc.hset('testdict','a','1')
print rc.hget('testdict','b')