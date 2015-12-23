# coding:utf8

import dao.RedisDAO
from util.Util import Config
config = Config()
redis_connect = dao.RedisDAO.connect(config.reidsIP)

def pushTask(detailTask):
    return dao.RedisDAO.publishTask(redis_connect,detailTask)


if __name__ == '__main__':
    pushTask()