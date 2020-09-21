import logging

from proxypool.database import RedisClient
from proxypool.crawler import Crawler
from proxypool.settings import *


class Getter:
    """
    A class that can collect ip proxies and put them into redis
    """

    def __init__(self):
        self.redis = RedisClient()
        self.crawler = Crawler()
        self.logger = logging.getLogger('main.getter')
        self.proxy_list = []


    def collect(self):
        """
        Collect proxies into a list using the functions from self.crawler.
        return: a list of proxies
        """
        for callback_label in range(self.crawler.__CrawlFuncCount__):
            try:
                count = 0
                self.logger.info(f"Start crawling with function {callback_label}...")
                callback = self.crawler.__CrawlFunc__[callback_label]
                proxies = self.crawler.get_proxies(callback)
            except Exception as e:
                self.logger.exception(str(e.args))
            else:
                count += len(proxies)
                self.proxy_list.extend(proxies)
                self.logger.info(f'Got {count} proxies with function {callback_label}')


    def store(self, redis_key=REDIS_KEY):
        """
        Put proxies into redis
        """
        if not self.redis.is_over_threshold() and self.redis.acquire_lock():
            saved = self.redis.add_proxies(self.proxy_list, key=redis_key)
            self.redis.release_lock()
            return saved
        else:
            self.logger.info("Failed to add collected proxies into database due to either is_over_threshold or failed to acquire_lock")
            self.redis.release_lock()
            return 0

    def run(self):
        """
        Start collecting and then store result into redis
        """
        self.collect()
        self.store()

