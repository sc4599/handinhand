# -*- coding:utf-8 –*-

import time
from qiniu import Auth,put_data,put_file,etag
import hashlib
import json
import urllib2

class Umeng(object):
    def md5(self,s):
        m = hashlib.md5(s)
        return m.hexdigest()


    def push_unicast(self,appkey, app_master_secret, device_token):
        timestamp = int(time.time() * 1000 )
        method = 'POST'
        url = 'http://msg.umeng.com/api/send'
        params = {'appkey': appkey,
                  'timestamp': timestamp,
                  'device_tokens': device_token,
                  'type': 'unicast',
                  'payload':
                      {'body':
                           {'ticker': 'Hello World',
                                       'title':'nihao',
                                       'text':'qiupubin ni hao',
                                       'after_open': 'go_app'
                            },
                        'display_type': 'notification'
                  }
        }
        post_body = json.dumps(params)
        print post_body
        sign = self.md5('%s%s%s%s' % (method,url,post_body,app_master_secret))
        try:
            r = urllib2.urlopen(url + '?sign='+sign, data=post_body)
            print r.read()
        except urllib2.HTTPError,e:
            print e.reason,e.read()
        except urllib2.URLError,e:
            print e.reason

class Qiniu(object):
    def __init__(self,access_key,secret_key,bucket_name):
        self.bucket_name = bucket_name
        self.q = Auth(access_key, secret_key)

    def getupToken(self):
        # 直接上传二进制流

        key = 'nihao'
        data = u'hello bubby!'
        token = self.q.upload_token(self.bucket_name,)
        ret, info = put_data(token, key, data,)
        print 'getupToken info = ',info
        # assert ret['key'] == key
        # token2 = self.q.upload_token(self.bucket_name, key, 7200, {'callbackUrl':"http://callback.do", 'callbackBody':"name=$(fname)&hash=$(etag)"})
        return token

    def upToken2(self):
        key = ''
        data = 'hello bubby!'
        token = self.q.upload_token(self.bucket_name, key,)
        ret, info = put_data(token, key, data, mime_type="application/octet-stream", check_crc=True)
        print(info)
        assert ret['key'] == key

    # 上传本地文件
    def uploaclFile(self):
        filePath = 'D:\\qiupubin.jpg'
        key = 'test_file'

        token = self.q.upload_token(self.bucket_name, key,)
        ret, info = put_file(token, key,filePath, check_crc=True)
        print(info)
        assert ret['key'] == key
        pass


if __name__ == '__main__':
    access_key = 'Q6OQ-uObfqSK65T-v9WuJTrQJIYigBkDdI5-wqJz'
    secret_key = 'no-ZxV1TnVQ6ZJAqXr-tp0xoYOokcIE_g76weLjX'
    bucket_name = 'handinhand'
    q = Qiniu(access_key,secret_key,bucket_name)
    print ''

