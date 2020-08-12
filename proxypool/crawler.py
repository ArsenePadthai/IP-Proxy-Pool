import re
import logging
import random
import time

import requests
from pyquery import PyQuery as pq

from requests.exceptions import ConnectionError
from random_useragent.random_useragent import Randomize

r_agent = Randomize()
platform = ['windows', 'mac', 'linux']

headers = {
    'User-Agent': '',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'
}

PROXY_PATTERN = '[1-9]\d{0,2}\.[1-9]\d{0,2}\.[1-9]\d{0,2}\.[1-9]\d{0,2}:\d+'


class ProxyMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        count = 0
        attrs['__CrawlFunc__'] = []
        for k, v in attrs.items():
            if 'crawl_' in k:
                attrs['__CrawlFunc__'].append(k)
                count += 1
        attrs['__CrawlFuncCount__'] = count
        return type.__new__(mcs, name, bases, attrs)


# TODO: Refactor code to reduce duplicated code.
class Crawler(object, metaclass=ProxyMetaclass):
    def __init__(self):
        self.logger = logging.getLogger('main.crawler')

    def get_proxies(self, callback):
        proxies = []
        for proxy in eval("self.{}()".format(callback)):
            proxies.append(proxy)
        return proxies

    def get_page(self, url):
        random_user_agent = r_agent.random_agent('desktop', random.choice(platform))
        headers['User-Agent'] = random_user_agent
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            self.logger.exception(str(e.args))
            return None


    def crawl_free_proxy_list_net(self):
        """
        Crawl from free-proxy-list.net.
        :return: string. xxx.xxx.xxx.xxx:xxxxx
        """
        base_url = 'https://free-proxy-list.net'
        html = self.get_page(base_url)
        count = 0
        if html:
            items = re.findall(PROXY_PATTERN, html, flags=re.A)
            for i in items:
                count += 1
                yield i
        self.logger.info(f'free-proxy-list.net: got {count} proxies.')


    def crawl_proxyrack(self):
        """
        Crawl from www.proxyrack.com.
        :return: string. xxx.xxx.xxx.xxx:xxxxx
        """
        base_url = "https://www.proxyrack.com/proxyfinder/proxies.json"
        perPage = 100
        online = -1
        count = 0
        for i in range(0, 10):
            offset = i * perPage
            payload = {
                'sorts[online]': online,
                'perPage': perPage,
                'offset': offset
            }
            res = requests.get(base_url, params=payload)
            if res.status_code == 200:
                items = res.json().get("records")
                for _ in items:
                    count += 1
                    yield _['ip'] + ':' + _['port']
        self.logger.info(f'www.proxyrack.com: got {count} proxies.')
