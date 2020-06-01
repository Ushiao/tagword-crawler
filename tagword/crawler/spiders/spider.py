# -*- coding:utf-8 -*-
# Name: 
# Description: 
# Contact: contact@tagword.cn
# =========================================================
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import random
import http.cookiejar as cookielib
from requests import Request, Session
from urllib.parse import urlparse

from tagword.crawler.spiders.ua import USER_AGENTS


class SpiderProto(object):
    def __init__(self, proxies={}, timeout=5, headers=None, stream=False, verify=False, cert=()):
        """
        初始化爬虫
        :param proxies: 代理信息
        :param timeout: 超时时间
        :param headers: 头信息
        :param stream: 持续下载
        :param verify: 验证SSL
        :param cert: 验证证书
        """
        self.proxies = proxies
        self.timeout = timeout
        self.stream = stream
        self.verify = verify
        self.cert = cert
        self.headers = {
            'Host': None,
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': random.choice(USER_AGENTS)['ua'],
            'Accept': 'text/html,application/xhtml+xml,application/xml,application/json; */*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        } if headers is None else headers

    def set_random_user_agent(self):
        self.headers['User-Agent'] = random.choice(USER_AGENTS)['ua']

    def set_user_agent(self, ua):
        self.headers['User-Agent'] = ua

    def fetch(self, url=None, params=None, data=None, cookies=None, method="GET"):
        parsed_uri = urlparse(url)
        host = parsed_uri.netloc
        self.headers['Host'] = host
        req = Request(method=method,
                      url=url,
                      params=params,
                      data=data,
                      cookies=cookies,
                      headers=self.headers)
        session = Session()
        prepped = session.prepare_request(req)
        resp = session.send(
            prepped,
            stream=self.stream,  # 抓取流文件或者大文件使用
            verify=self.verify,  # #verify是否验证服务器的SSL证书
            proxies=self.proxies,
            cert=self.cert,
            timeout=self.timeout
        )
        return resp
