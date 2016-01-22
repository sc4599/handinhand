# coding:utf-8
# http://192.168.1.124:9080/doctors
import json
import urllib2
import dao.RedisDAO

class UserOnLineControl(object):
    def __init__(self,url,redis_connect):
        self.url = url
        self.redis_connect = redis_connect


    def getDoctorsOnline(self):
        req = urllib2.Request(self.url, )
        print 'current pushTask req =', req
        response = urllib2.urlopen(req)
        res = response.read()

        return json.loads(res)

    def getDoctorsOnlineEntity(self):

        doctors = self.getDoctorsOnline()
        print doctors
        doctorsEntity = []
        for i in doctors:
            s= self.redis_connect.hgetall('hash_doctor_%s'%i)
            doctorsEntity.append(s)
        return json.dumps(doctorsEntity)



if __name__ == '__main__':
    rc = dao.RedisDAO.connect('192.168.1.18')
    url = 'http://192.168.1.124:9080/doctors'
    c = UserOnLineControl(url,rc)
    r = c.getDoctorsOnlineEntity()
    print r