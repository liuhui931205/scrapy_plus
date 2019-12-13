# -*-coding:utf-8-*-
from scrapy_plus.https.request import Request
# from .spider import Spider

from datetime import datetime
from scrapy_plus.utils.log import logger
from scrapy_plus.conf import settings
import importlib
import time
if settings.ASYNC_TYPE == "thread":
    from multiprocessing.dummy import Pool
elif settings.ASYNC_TYPE == "coroutine":
    from scrapy_plus.async.coroutine import Pool
else:
    raise Exception("不支持的异步类型：%s, 只能是'thread'或者'coroutine'" % settings.ASYNC_TYPE)

from .scheduler import Scheduler
from .downloader import Downloader


class Engine(object):

    def __init__(self):

        self.spiders = self._auto_import_instances(settings.SPIDERS, True)
        self.scheduler = Scheduler()
        self.downloader = Downloader()
        self.pipelines = self._auto_import_instances(settings.PIPELINES)
        self.spider_mids = self._auto_import_instances(settings.SPIDER_MIDDLEWARES)
        self.downloader_mids = self._auto_import_instances(settings.DOWNLOADER_MIDDLEWARES)

        self.total_response_number = 0

        self.pool = Pool()
        self.running = False

    def start(self):
        start = datetime.now()
        logger.info("开始运行时间：{}".format(start))
        self._start_engine()
        stop = datetime.now()
        logger.info("结束运行时间：{}".format(stop))
        logger.info("耗时：%.2f" % (stop - start).total_seconds())

    def _start_engine(self):
        self.running = True
        if settings.ROLE is None or settings.ROLE == "master":

            self.pool.apply_async(self._start_requests, error_callback=self._error_callback)
        if settings.ROLE is None or settings.ROLE == "slave":

            for i in range(settings.MAX_ASYNC_NUMBER):
                self.pool.apply_async(self._execute_request_response_item,
                                      callback=self._callback,
                                      error_callback=self._error_callback)
        while 1:
            time.sleep(0.0001)
            # self._execute_request_response_item()
            if self.total_response_number >= self.scheduler.total_request_number and self.scheduler.total_request_number != 0:
                self.running = False
                break
        self.pool.close()
        self.pool.join()

    def _start_requests(self):
        for spider_name, spider in self.spiders.items():
            for start_request in spider.start_requests():
                for spider_mid in self.spider_mids:

                    start_request = spider_mid.process_request(start_request)
                start_request.spider_name = spider_name
                self.scheduler.add_request(start_request)

    def _execute_request_response_item(self):
        request = self.scheduler.get_request()
        if request is None:
            return
        for downloader_mid in self.downloader_mids:
            request = downloader_mid.process_request(request)
        response = self.downloader.get_response(request)
        for downloader_mid in self.downloader_mids:
            response = downloader_mid.process_response(response)
        spider = self.spiders[request.spider_name]
        parse = getattr(spider, request.parse)
        results = parse(response)
        # results.meta = request.meta
        for result in results:
            if isinstance(result, Request):
                for spider_mid in self.spider_mids:
                    result = spider_mid.process_request(result)
                result.spider_name = request.spider_name
                self.scheduler.add_request(result)
            else:
                for spider_mid in self.spider_mids:
                    result = spider_mid.process_item(result)
                for pipeline in self.pipelines:
                    result = pipeline.process_item(result)

        self.total_response_number += 1

    def _callback(self, temp):
        if self.running is True:
            self.pool.apply_async(self._execute_request_response_item, callback=self._callback)

    def _error_callback(self, exception):
        try:
            raise exception
        except Exception as e:
            logger.exception(e)

    def _auto_import_instances(self, path=[], isspider=False):

        if isspider is True:
            instances = {}
        else:
            instances = []

        for p in path:
            module_name = p[:p.rfind(".")]
            cls_name = p[p.rfind(".") + 1:]
            ret = importlib.import_module(module_name)
            cls = getattr(ret, cls_name)

            if isspider is True:
                instances[cls.name] = cls()
            else:
                instances.append(cls())

        return instances
