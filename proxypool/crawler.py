import logging
import random
import requests
from bs4 import BeautifulSoup
from random_useragent.random_useragent import Randomize
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from proxypool.base import Proxy

r_agent = Randomize()
platform = ['windows', 'mac', 'linux']

headers = {
    'User-Agent': '',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'
}


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
                return response
        except Exception as e:
            self.logger.exception(str(e.args))
            return None


    def crawl_free_proxy_list_net(self):
        """
        Crawl from free-proxy-list.net.
        :return: string. http://xxx.xxx.xxx.xxx:xxxx__FreeProxyListNet or https://...
        """
        base_url = 'https://free-proxy-list.net'

        r = self.get_page(base_url)
        page = BeautifulSoup(r.content, 'html.parser')

        tables = page.find_all(id='proxylisttable')

        assert len(tables) == 1

        table = tables[0]
        for row in table.find_all('tr'):
            proxy = [td.string for td in row.find_all('td')]
            if proxy and proxy[4] == "elite proxy":
                prefix = 'http' if proxy[6] == "no" else "https"
                yield Proxy(prefix, proxy[0], proxy[1], "FreeProxyListNet")


    def crawl_free_proxy_list_net2(self):
        """
        Crawler from freeproxylists.net
        :return: string. http://xxx.xxx.xxx.xxx:xxxx__FreeProxyListNet2 or https://...
        """
        driver = webdriver.Remote(command_executor='http://127.0.0.1:8910',
                desired_capabilities=DesiredCapabilities.PHANTOMJS)
        # country=all, port=all, protocol=all, anonymity=high, uptime>60%
        driver.get('https://freeproxylists.net/?c=&pt=&pr=&a%5B%5D=2&u=60')
        driver.implicitly_wait(2)
        html = driver.page_source
        driver.quit()

        page = BeautifulSoup(html, 'html.parser')
        table = page.find_all("table")[1]

        for row in table.find("tbody").find_all("tr")[1:]:
            tds = row.find_all("td")
            if len(tds) < 2:
                continue
            ip = tds[0].find("a").string
            port = tds[1].string
            prefix = tds[2].string.lower()
            yield Proxy(prefix, ip, port, "FreeProxyListNet2")

