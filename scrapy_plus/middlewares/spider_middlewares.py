# -*-coding:utf-8-*-


class SpiderMiddleware(object):

    def process_request(self, request):

        print("这是爬虫中间件：process_request方法")
        return request

    def process_item(self, response):
        print("这是爬虫中间件：process_item方法")
        return response
