# -*-coding:utf-8-*-


class Item(object):

    def __init__(self, data):
        self._data = data

    @property
    def data(self):
        return self._data
