# coding:utf8


def ab():
    print '11111'

import dao.RedisDAO
rc = dao.RedisDAO.connect('192.168.1.18')


l  = ['private_hash_detailTask_13887083253','private_hash_detailTask_13887083254','private_hash_detailTask_13887083255']

l2 = [i[-11:] for  i in l]

r = rc.keys('channel*')
rc.delete()
rc.exists()
print r