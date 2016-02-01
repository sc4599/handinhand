# coding:utf-8
# 消息控制



class pushTaskMessage(object):
    def __init__(self,redis_connect):
        self.redis_connect = redis_connect
        self.messageKEY = 'off_line_message'
    def getOffLineMessage(self,userID):
        messages = self.redis_connect.hget(userID,self.messageKEY)
        if messages == None or messages == 'None':
            messages=[]
        return messages

    def saveMessageIfNotOnLine(self,userID,data):
        r =self.redis_connect.hset(userID,self.messageKEY,data)
        if r ==1:
            return True
        else:
            return False

    def removeOffLineMessage(self,userID):
        self.redis_connect.lrem(userID,self.messageKEY)

