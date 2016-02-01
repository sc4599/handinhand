# coding:utf-8
from dao import RedisDAO
from control.TaskControl import pushTask
import time
import json


class PrivateLetterControl(object):
    def __init__(self,redis_connect):
        self.redis_connect = redis_connect
        pass

    # 病人发送私信
    def sendPrivateLetter(self,detailTask,doctor_tel):
        # 0.判断病人私信条数是否大于=10
        privateLetterCount = len(self.redis_connect.keys('private_hash_detailTask_%s_*'%detailTask.get('patient_tel')))
        print 'this is sendPrivateLetter privateLetterCount=',privateLetterCount
        if privateLetterCount>10:
            return '200601'# 您的私信数量达到10条，请待处理后再发信的私信

        # 1.生成私信hash_privateLetter_tel 哈希表
        detailTask['id'] = 'private_hash_detailTask_%s_%s' % (detailTask.get('patient_tel'), int(time.time()))
        self.redis_connect.hmset(detailTask.get('id'),detailTask)
        # 2.医生私信记录增加私信id
        print 'this is sendPrivateLetter doctor_tel=',doctor_tel
        print
        if self.redis_connect.exists('hash_doctor_%s'%doctor_tel)==False:
            return '200604' # 发送私信医生不存在
        privateLetterListjson = self.redis_connect.hget('hash_doctor_%s'%doctor_tel,'private_letter_list')
        if privateLetterListjson == None or privateLetterListjson =='None':
            privateLetterList=[]
        else:
            # 2。1 判断病人是否已经给当前医生发过私信
            privateLetterList = json.loads(privateLetterListjson)
            privateLetterTels = [i[-11:] for i in privateLetterList]
            if detailTask.get('id') in privateLetterTels:
                return '200602' # 您已经给当前医生发过私信，请等待处理后重新发送
        privateLetterList.append(detailTask.get('id'))
        self.redis_connect.hset('hash_doctor_%s'%doctor_tel,'private_letter_list',json.dumps(privateLetterList))
        #2.2 在私信实体中添加 发送给谁字段 （sendto）
        self.redis_connect.hset(detailTask.get('id'),'sendTo','hash_doctor_%s'%doctor_tel)

        # 3.通知医生有信给你
        r =pushTask(what='sendPrivateLetter',doctor_tel=doctor_tel,channelTaskID=detailTask.get('id'))
        if r !='10001':
            return r
        return '100102 ' # 私信发送成功

    # 医生接受私信
    def acceptPrivateLetter(self,detailTask,doctor_tel):
        # 1.医生电话号码添加到 私信哈希表中
        self.redis_connect.hset(detailTask.get('id'),'doctor_tel',doctor_tel)
        # 2.通知病人医生接受了你的私信，显示医生电话号码
        r = pushTask('acceptPrivateLetter',patient_tel=detailTask.get('patient_tel'),doctor_tel=doctor_tel, channelTaskID=detailTask.get('id'))
        if r != '10001':
            return r

        # 3.下一步等待电话或主动联系（等ing）

        # 4.医生私信列表添加当前私信ID
        return '100104'# 接受私信成功

    # 医生确定接受私信为病人治疗
    def confirmPrivateLetter(self,detailTask):
        # 1.私信哈希表，生成任务记录（hash_detailTask_tel)哈希表
        privateLetterTask = self.redis_connect.hgetall(detailTask.get('id'))
        print 'this is confirmPrivateLetter privateLetterTask=',privateLetterTask
        self.redis_connect.hmset(detailTask.get('id')[8:],privateLetterTask)
        # 2.病人私信记录删除此私信ID
        self.redis_connect.delete(detailTask.get('id'))
        # 2.1 医生私信记录删除此私信ID
        privateLetterList = json.loads(self.redis_connect.hget('hash_doctor_%s'%detailTask.get('doctor_tel'),'private_letter_list'))
        if detailTask.get('id') in privateLetterList:
            privateLetterList.remove(detailTask.get('id'))
        self.redis_connect.hset('hash_doctor_%s'%detailTask.get('doctor_tel'),'private_letter_list',json.dumps(privateLetterList))
        # 3.医生行医记录里追加此任务id（Treatment_count）
        r = self.redis_connect.hget('hash_doctor_%s'%detailTask.get('doctor_tel'),'treatment_count')
        if r =='None' or r == None:
            treatments = []
        else:
            treatments = json.loads(r)
        treatments.append(detailTask.get('id')[8:])
        self.redis_connect.hset('hash_doctor_%s'%detailTask.get('doctor_tel'),'treatment_count',json.dumps(treatments))
        # 4.病人就医记录里添加详细任务id（medical_history）
        r = self.redis_connect.hget('hash_patient_%s'%detailTask.get('patient_tel'),'medical_history')
        if r =='None' or r == None:
            medicalHistorys = []
        else:
            medicalHistorys  = json.loads(r)
        medicalHistorys.append(detailTask.get('id')[8:])
        self.redis_connect.hset('hash_patient_%s'%detailTask.get('patient_tel'),'medical_history',json.dumps(medicalHistorys))
        # 5.通知病人医生最终确定了你的私信
        r = pushTask('confirmPrivateLetter',patient_tel=detailTask.get('patient_tel'),channelTaskID=detailTask.get('id'))
        if r != '10001':
            return r
        return '100105' # 确定私信成功

    # 医生取消私信，拒绝病人此次请求
    def cancelTaskPrivateLetter(self,detailTask,doctor_tel):

        # 1.通知病人医生拒绝了你的私信
        r =pushTask('cancelTaskPrivateLetter',patient_tel=detailTask.get('patient_tel'),channelTaskID=detailTask.get('id'))
        if r != '10001':
            return r
        # 3.医生私信列表删除此私信ID
        privateLetterList = json.loads(self.redis_connect.hget('hash_doctor_%s'%doctor_tel,'private_letter_list'))
        print 'this is cancelTaskPrivateLetter privateLetterList =',privateLetterList
        print 'this is cancelTaskPrivateLetter detailTask.get(id) in privateLetterList =',detailTask.get('id') in privateLetterList
        if detailTask.get('id') in privateLetterList:
            privateLetterList.remove(detailTask.get('id'))
        print 'this is cancelTaskPrivateLetter privateLetterList =',privateLetterList
        self.redis_connect.hset('hash_doctor_%s'%doctor_tel,'private_letter_list',json.dumps(privateLetterList))
        # 2.删除私信哈希表
        r = self.redis_connect.delete(detailTask.get('id'))
        if r != 1:
            return '' # 无当前任务ID
        return '100103' # 取消私信成功


    # 医生请求自己的私信列表
    # @doctor_tel 医生电话
    # @return 当前医生所有私信实例列表
    def queryDoctorPrivateLetterList(self,doctor_tel):
        privateLetterListjson = self.redis_connect.hget('hash_doctor_%s'%doctor_tel,'private_letter_list')
        print privateLetterListjson
        privateLetterEntityList = []
        if privateLetterListjson == None or privateLetterListjson =='None':
            privateLetterList=[]
        else:
            privateLetterList = json.loads(privateLetterListjson)
        for i in  privateLetterList:
            entity = self.redis_connect.hgetall(i)
            privateLetterEntityList.append(entity)
        return json.dumps(privateLetterEntityList)

    # 病人请求自己私信列表
    # @patient 病人电话
    # @return 当前病人所有私信实例列表
    def queryPatientPrivateLetterList(self,patient_tel):
        privateLetterList = self.redis_connect.keys('private_hash_detailTask_%s_*'%patient_tel)
        privateLetterEntityList = []
        for i in privateLetterList:
            privateLetterEntityList.append(self.redis_connect.hgetall(i))

        return json.dumps(privateLetterEntityList)

    # 根据任务ID 查任务信息
    def queryPrivateLetterByID(self,detailTaskID):
        r = self.redis_connect.hgetall(detailTaskID)
        return json.dumps(r)

