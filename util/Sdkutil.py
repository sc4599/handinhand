# coding = utf-8

import time

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
    pass


if __name__ == '__main__':
    print ''

    # appkey = '5683510267e58e60e7000a3f'
    # app_master_secret = 'nkk8lb8zioq9hq3p1evcms5lykd2guut'
    # device_token = 'Apu7mfC-b5-SiLdAXOBKZZLOSqnn91pNoWcsya7ZwHqY'
    #
    # Umeng().push_unicast(appkey, app_master_secret, device_token)
