# -*-coding:utf-8-*-

from gevent.pool import Pool as BasePool
import gevent.monkey

gevent.monkey.patch_all()


class Pool(BasePool):

    def apply_async(self, func, args=None, kwds=None, callback=None, error_callback=None):
        return super().apply_async(func, args=args, kwds=kwds, callback=callback)

    def close(self):
        pass