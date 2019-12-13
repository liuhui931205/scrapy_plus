# -*-coding:utf-8-*-
from six.moves.queue import Queue
from hashlib import sha1
import w3lib.url
from scrapy_plus.utils.log import logger
from scrapy_plus.conf import settings
from scrapy_plus.queue import Queue as RedisQueue
from scrapy_plus.set import NoramlFilterContainer, RedisFilterContainer



def utf8_string(string):
    import six
    if six.PY2:
        if isinstance(string, str):
            return string
        else:
            return string.encode("utf-8")

    elif six.PY3:
        if isinstance(string, str):
            return string.encode("utf-8")
        else:
            return string


class Scheduler(object):

    def __init__(self):
        if settings.ROLE is None:
            self.queue = Queue()
            self._filter_container = NoramlFilterContainer()
        elif settings.ROLE == "master" or settings.ROLE == "slave":
            self.queue = RedisQueue()
            self._filter_container = RedisFilterContainer()
        self.total_request_number = 0
        # self._filter_container = set()
        self.repeat_request_number = 0

    def add_request(self, request):
        
        fp = self._gen_fp(request)
        if not self.filter_request(fp, request):
            self.queue.put(request)
            logger.info("添加请求成功[%s %s]"%(request.method, request.url))
            self._filter_container.add_fp(fp)
            self.total_request_number += 1
        else:
            self.repeat_request_number += 1

    def get_request(self):
        try:
            request = self.queue.get(False)
        except:
            return None
        else:
            return request

    def filter_request(self, fp, request):

        if self._filter_container.exists(fp):
            logger.info("发现重复的请求：%s" % (request.url))
            return True
        else:
            return False

    def _gen_fp(self, request):
        url = w3lib.url.canonicalize_url(request.url)
        method = request.method.upper()
        params = request.params if request.params is not None else {}
        params = sorted(params.items(), key=lambda x: x[0])

        data = request.data if request.data is not None else {}
        data = sorted(data.items(), key=lambda x: x[0])
        s1 = sha1()
        s1.update(utf8_string(url))
        s1.update(utf8_string(method))
        s1.update(utf8_string(str(params)))
        s1.update(utf8_string(str(data)))
        fp = s1.hexdigest()
        return fp
