#coding=utf-8

from aliyunsdkcore import client
from aliyunsdksts.request.v20150401 import AssumeRoleRequest
# AccessKeyId
# kbR5rBjY7jmIrPWU
# AccessKeySecret
# 9FB8nYmm1goAOGH6PMFovyjSHjZqih

# 构建一个 Aliyun Client, 用于发起请求
# 构建Aliyun Client时需要设置AccessKeyId和AccessKeySevcret
# STS是Global Service, API入口位于杭州, 这里Region填写"cn-hangzhou"
clt = client.AcsClient('<access-key-id>','<access-key-secret>','cn-hangzhou')

# 构造"AssumeRole"请求
request = AssumeRoleRequest.AssumeRoleRequest()
# 指定角色
request.set_RoleArn('<role-arn>')
# 设置会话名称，审计服务使用此名称区分调用者
request.set_RoleSessionName('<role-session-name>')

# 发起请求，并得到response
response = clt.do_action(request)

print response


# AccessKeyID：
# slr8fcEAJyHRnuP5
# AccessKeySecret：
# dCk6vuhbeDX1hdLERefENnzylQVwy2

import oss2
class AliOss2(object):
    def __init__(self):
        self.AccessKeyID ='CdfqvJaiSLv4fq74'
        self.AccessKeySecret = 'VKT8ObzbMXt3Dklj2IS4xUYMXUBXcM '
        self.auth = oss2.Auth(self.AccessKeyID,self.AccessKeySecret)
        self.service = oss2.Service(self.auth,'oss-cn-shenzhen.aliyuncs.com')

    # 获取oss 上所有 bucket
    def getBuckets(self):
        print ([b.name for b in oss2.BucketIterator(self.service)])

    # 建立一个 bucket
    def createBucket(self,endpoint='http://oss-cn-shenzhen.aliyuncs.com',bucketName='handinhand2'):
        bucket = oss2.Bucket(self.auth,endpoint, bucketName)
        bucket.create_bucket(oss2.models.BUCKET_ACL_PRIVATE)