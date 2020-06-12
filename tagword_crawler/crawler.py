# -*- coding:utf-8 -*-
# Name: 
# Description: 
# Contact: contact@tagword_crawler.cn
# =========================================================
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import random
from queue import Queue
import threading
import time

import pkgutil
import importlib
from urllib.parse import urlparse


def create_crawler():
    app = TGWCrawler()
    for pkg in pkgutil.walk_packages(sys.path):
        if pkg.ispkg:
            if pkg.name.startswith("tagword_crawler_"):
                p = importlib.import_module(pkg.name)
                app.register_spider(p.main[1:], url_host=p.main[0])
    return app


class TGWCrawler(object):
    def __init__(self):
        self.__spiders = {}
        self.__proxies = {}

    def register_spider(self, spiders, url_host):
        for spider in spiders:
            self.__spiders[url_host] = self.__spiders.get(url_host, []) + [spider]

    def register_proxy(self, proxies):
        self.__proxies = proxies

    def multi_fetch(self, items, threads_num=4):
        q = Queue()
        p = Queue()
        for item in items:
            q.put(item)
        threads = []
        for i in range(0, threads_num):
            t = threading.Thread(target=self.__fetch, args=(q, p))
            threads.append(t)
        for t in threads:
            t.setDaemon(True)
            t.start()
        for thread in threads:
            thread.join()

        output = []
        while not p.empty():
            item = p.get()
            output.append(item)
        return output

    def fetch(self, items):
        output = []
        for item in items:
            source = item['source']
            result = self._fetch(**item)
            if result is None:
                continue
            for item in result:
                item['source'] = source
                output.append(item)
            time.sleep(random.randint(1, 5))
        return output

    def __fetch(self, q, p):
        while not q.empty():
            item = q.get()
            source = item['source']
            result = self._fetch(**item)
            if result is None:
                continue
            for item in result:
                item['source'] = source
                p.put(item)
            time.sleep(random.randint(1, 5))

    def _fetch(self, **kwargs):
        parsed_uri = urlparse(kwargs.get("url"))
        host = parsed_uri.netloc
        schema = parsed_uri.scheme
        spiders = self.__spiders.get(host, None)
        if spiders is None:
            return None
        spider = None
        if len(spiders) == 1:
            spider = spiders[0]
        elif len(spiders) > 1:
            for spider in spiders:
                if spider.__name__ == kwargs.get("spider"):
                    break
        if spider is None:
            return None

        spider = spider()
        # 设置ssl验证
        if schema == 'https':
            spider.verify = True
        if schema == 'http':
            spider.verify = False

        # 设置代理
        if self.__proxies:
            proxy = random.choice(self.__proxies[schema])
            spider.proxies = {schema: proxy}

        # 轮训相关页面
        try:
            result = spider.request(**kwargs)
        except:
            result = self._fetch(**kwargs)
        else:
            if self.__proxies:
                print(proxy)
        return result

