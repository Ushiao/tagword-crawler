# -*- coding:utf-8 -*-
# Name: 
# Description: 
# Contact: contact@tagword.cn
# =========================================================
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import random
from queue import Queue
import threading
import time

import pkgutil
import importlib
from urllib.parse import urlparse

from tagword.crawler import spiders


def create_crawler():
    app = TGWCrawler()
    for pkg in pkgutil.walk_packages(spiders.__path__):
        if pkg.ispkg:
            p = importlib.import_module("." + pkg.name, package="tagword.crawler.spiders")
            app.register_spider(p.main[1], url_host=p.main[0])
    return app


class TGWCrawler(object):
    def __init__(self):
        self.__spiders = {}
        self.__proxies = {}

    def register_spider(self, spider, url_host):
        self.__spiders.update({url_host: spider})

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

    def fetch(self, **kwargs):
        return self._fetch(**kwargs)

    def __fetch(self, q, p):
        while not q.empty():
            item = q.get()
            result = self._fetch(**item)
            if result is None:
                continue
            for item in result:
                p.put(item)
            time.sleep(random.randint(1, 5))

    def _fetch(self, **kwargs):
        parsed_uri = urlparse(kwargs.get("url"))
        host = parsed_uri.netloc
        schema = parsed_uri.scheme
        spider = self.__spiders.get(host, None)
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


if __name__ == "__main__":

    # 准备连接
    items = [
        {"url": "http://www.meituan.com/zhoubianyou/93311902/", "pagenum": 0},
        {"url": "http://piao.ctrip.com/ticket/dest/t1412255.html", "pagenum": 0},
        {"url": "http://piao.ctrip.com/ticket/dest/t762.html", "pagenum": 0},
        {"url": "http://piao.ctrip.com/ticket/dest/t1816019.html", "pagenum": 0},
        {"url": "http://piao.ctrip.com/ticket/dest/t4651499.html", "pagenum": 0},
        {"url": "http://hotels.ctrip.com/hotel/48565681.html", "pagenum": 0},
    ]

    # inf = open("../proxy/proxies.list", "r")
    # proxies = {"http": [], "https": []}
    # for line in inf:
    #     item = json.loads(line)
    #     if item['valid'] == False:
    #         continue
    #     proxies[item['schema'].lower()].append("%s://%s:%s" % (item['schema'].lower(), item['ip'], item['port']))

    crawler = create_crawler()
    # crawler.register_proxy(proxies)
    result = crawler.multi_fetch(items)
    for i in result:
        print(i)
