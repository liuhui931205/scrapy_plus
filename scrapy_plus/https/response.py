# -*-coding:utf-8-*-
import re
import json
from lxml import etree


class Response(object):

    def __init__(self, url, status_code, headers, body):
        self.url = url
        self.status_code = status_code
        self.headers = headers
        self.body = body

    def xpath(self, rule):
        html = etree.HTML(self.body)
        return html.xpath(rule)

    @property
    def json(self):
        return json.loads(self.body)

    def re_findall(self, rule, data=None):
        if data is None:
            data = self.body
        return re.findall(rule, data)
