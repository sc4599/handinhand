# coding:utf8


import dao.RedisDAO
import json
rc =dao.RedisDAO.connect('192.168.1.18')
#
# r= rc.hget('hash_doctor_15888271828','current_task_count')
# l = json.loads(r)
l = ['a']

print l.remove('b')