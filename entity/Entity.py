# coding:utf8
class Task(object):
    def __init__(self):
        self.id = None
        self.taskName = ''
        self.symptom = ''
        self.lon = ''
        self.lat = ''


class DetailTask(object):
    def __init__(self):
        self.id = None
        self.symptom = 'symptom'
        self.type = 'type'
        self.datetime = 'datetime'
        self.lon = 'lon'
        self.lat = 'lat'
        self.patient_name = 'patient_name'
        self.patient_tel = 'patient_tel'
        self.doctor_name= 'doctor_name'
        self.doctor_tel= 'doctor_tel'
        self.comment_id= 'comment_id'

# 所有 用于存储key的list的键
class ListInfo(object):
    def __init__(self):
        self.list_handinhand_doctor = ''

class doctor(object):
    def __init__(self):
        self.tel='tel'
        self.name=''
        self.gender=''
        self.pic=''
        self.age=''
        self.collection_count=''
        self.comment_count=''
        self.treatment_count=''
        self.qualification=''


class patient(object):
    def __init__(self):
        self.tel=''
        self.name=''
        self.pic=''
        self.gender=''
        self.age=''
        self.treatment_count=''
        self.collication_list=''


if __name__ == '__main__':
    t = DetailTask()
    t.id = 1
    t2 = DetailTask()
    t2.id = 2
    t3 = DetailTask()
    t3.id = 3
    list = [t, t2, t3]
    for l in list:
        print l.id
    print t.doctor
