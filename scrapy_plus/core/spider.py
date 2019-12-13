# -*-coding:utf-8-*-
from scrapy_plus.items.item import Item
from scrapy_plus.https.request import Request


class Spider(object):

    start_url = []

    def start_requests(self):
        for url in self.start_url:
            yield Request(url)

    def parse(self, response):

        yield Item(response.body)
