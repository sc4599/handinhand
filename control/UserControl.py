# coding:utf-8
# http://192.168.1.124:9080/doctors
import json
import urllib2
import dao.RedisDAO
from util.distanceUtil import baiduDistance


class UserOnLineControl(object):
    def __init__(self, url, redis_connect):
        self.url = url
        self.redis_connect = redis_connect
        self.baiduDistance = baiduDistance()

    def getDoctorsOnline(self):
        req = urllib2.Request(self.url, )
        print 'current pushTask req =', req
        response = urllib2.urlopen(req)
        res = response.read()
        return json.loads(res)

    def getDoctorsOnlineEntity(self):
        doctors = self.getDoctorsOnline()
        print type(doctors)

        doctorsEntity = []
        print doctors
        for i in doctors:
            s = self.redis_connect.hgetall('hash_doctor_%s' % i)
            if 'current_task_count' in s:
                s.pop('current_task_count')
            if 'private_letter_list' in s:
                s.pop('private_letter_list')
            if 'treatment_count' in s:
                s.pop('treatment_count')
            doctorsEntity.append(s)
        return json.dumps(doctorsEntity)

    # 根据半径显示 周边医生
    def getDoctorBydistance(self, radius, lat_a, lng_a):
        alldoctorsKEY = self.redis_connect.keys('hash_doctor_*')
        alldoctorsEntitys = []
        for key in alldoctorsKEY:
            entity = self.redis_connect.hgetall(key)
            if 'location' in entity:
                print entity.get('location').split(' ')
                lat_b = float(entity.get('location').split(' ')[0])
                lng_b = float(entity.get('location').split(' ')[1])
                print 'lat_b = %s lng_b = %s '%(lat_b,lng_b)
                if self.baiduDistance.distanceFilter(radius, lat_a, lng_a, lat_b, lng_b):
                    alldoctorsEntitys.append(entity)
        return json.dumps(alldoctorsEntitys)


if __name__ == '__main__':
    rc = dao.RedisDAO.connect('192.168.1.18')
    url = 'http://192.168.1.124:9080/doctors'
    c = UserOnLineControl(url, rc)
    r = c.getDoctorBydistance(3000, 22.54186, 113.958915)
    # lo = ['22.54375','113.955578']
    # rc.hset('hash_doctor_18818684122','location',lo)
    # print json.dumps(rc.hgetall('hash_doctor_18818684122'))
    print r
