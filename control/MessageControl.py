# coding:utf-8
# 消息控制

import json

class pushTaskMessage(object):
    def __init__(self,redis_connect):
        self.redis_connect = redis_connect
        self.messageKEY = 'off_line_message'
    def getOffLineMessage(self,userID):
        messages = self.redis_connect.hget(userID,self.messageKEY)
        if messages == None or messages == 'None':
            messages='[]'
        return json.loads(messages)

    def saveMessageIfNotOnLine(self,userID,data):
        messages = self.getOffLineMessage(userID)
        messages.append(data)
        r =self.redis_connect.hset(userID,self.messageKEY,json.dumps(messages))
        if r:
            return True
        else:
            return False

    def removeOffLineMessage(self,userID,data):
        messages = self.getOffLineMessage(userID)
        if data in messages:
            messages.remove(data)
        else:
            return False
        r = self.redis_connect.hset(userID,self.messageKEY,json.dumps(messages))
        if r:
            return True
        else:
            return False

