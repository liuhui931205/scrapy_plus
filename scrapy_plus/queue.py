# -*-coding:utf-8-*-
import time
import pickle
import redis
from six.moves import queue as BaseQueue

REDIS_QUEUE_NAME = "request_queue"
REDIS_QUEUE_HOST = "10.11.5.165"
REDIS_QUEUE_PORT = 6379
REDIS_QUEUE_PASSWD = 123456
REDIS_QUEUE_DB = 6


class Queue(object):

    Empty = BaseQueue.Empty
    Full = BaseQueue.Full
    max_timeout = 0.3

    def __init__(self,
                 maxsize=0,
                 name=REDIS_QUEUE_NAME,
                 host=REDIS_QUEUE_HOST,
                 port=REDIS_QUEUE_PORT,
                 db=REDIS_QUEUE_DB,
                 lazy_limit=True,
                 password=REDIS_QUEUE_PASSWD):

        self.name = name
        self.redis = redis.StrictRedis(host=host, port=port, db=db, password=password)
        self.maxsize = maxsize
        self.lazy_limit = lazy_limit
        self.last_qsize = 0

    def qsize(self):
        self.last_qsize = self.redis.llen(self.name)
        return self.last_qsize

    def empty(self):

        if self.qsize() == 0:
            return True
        else:
            return False

    def full(self):
        if self.maxsize and self.qsize() >= self.maxsize:
            return True
        else:
            return False

    def put_nowait(self, obj):
        if self.lazy_limit and self.last_qsize < self.maxsize:
            pass
        elif self.full():
            raise self.Full
        self.last_qsize = self.redis.rpush(self.name, pickle.dumps(obj))
        return True

    def put(self, obj, block=True, timeout=None):
        if not block:
            return self.put_nowait(obj)
        start_time = time.time()
        while 1:
            try:
                return self.put_nowait(obj)
            except self.Full:
                if timeout:
                    lasted = time.time() - start_time
                    if timeout > lasted:
                        time.sleep(min(self.max_timeout, timeout - lasted))
                    else:
                        raise
                else:
                    time.sleep(self.max_timeout)

    def get_nowait(self):

        ret = self.redis.lpop(self.name)
        if ret is None:
            raise self.Empty

        return pickle.loads(ret)

    def get(self, block=True, timeout=None):
        if not block:
            return self.get_nowait()

        start_time = time.time()

        while 1:
            try:
                return self.get_nowait()
            except self.Empty:
                if timeout:
                    lasted = time.time() - start_time
                    if timeout > lasted:
                        time.sleep(min(self.max_timeout, timeout - lasted))
                    else:
                        raise
                else:
                    time.sleep(self.max_timeout)

