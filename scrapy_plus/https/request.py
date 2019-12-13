# -*-coding:utf-8-*-


class Request(object):

    def __init__(
            self,
            url,
            method="GET",
            headers={
                "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
            },
            params=None,
            data=None,
            spider_name="",
            parse='parse'):

        self.url = url
        self.method = method
        self.headers = headers
        self.params = params
        self.data = data
        self.parse = parse
        self.meta = None
        self.spider_name = spider_name
