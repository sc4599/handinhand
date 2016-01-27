# coding:utf-8
# latitude/ longitude 纬度/经度
# 中兴通讯 lon= 113.955578,lat=22.54375
# TCL           113.958848,    22.544852
# 中科大厦      113.959063,    22.543634
# 泰邦科技大厦  113.958915,    22.54186
import math
class baiduDistance(object):
    def getDistanceFromXtoY(self,lat_a, lng_a, lat_b, lng_b):
        pk = 180 / 3.1415926
        a1 = lat_a / pk
        a2 = lng_a / pk
        b1 = lat_b / pk
        b2 = lng_b / pk
        t1 = math.cos(a1) * math.cos(a2) * math.cos(b1) * math.cos(b2)
        t2 = math.cos(a1) * math.sin(a2) * math.cos(b1) * math.sin(b2)
        t3 = math.sin(a1) * math.sin(b1)
        tt = math.acos(t1 + t2 + t3)
        return 6366000 * tt

    def distanceFilter(self,radius,lat_a, lng_a, lat_b, lng_b):
        distance = self.getDistanceFromXtoY(lat_a, lng_a, lat_b, lng_b)
        if distance< radius:
            return True
        else:
            return False


if __name__=='__main__':
    lat_a =22.54375
    lng_a = 113.955578
    lat_b = 22.543634
    lng_b = 113.959063
    baidu = baiduDistance()
    r= baidu.getDistanceFromXtoY(lat_a,lng_a,lat_b,lng_b)
    print r