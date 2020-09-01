import sys
import asyncio
import logging

import aiohttp
import time

from proxypool.database import RedisClient
from proxypool.settings import *


class Tester:
    def __init__(self):
        # TODO recover
        # self.redis = RedisClient()
        self.redis = RedisClient(host='127.0.0.1')
        self.logger = logging.getLogger('main.tester')

    @staticmethod
    def check_anonymity(proxy, result):
        """
        Check if a specific proxy is anonymous
        :param proxy: ip address of the proxy.
        :param result: result acquired from test url.
        :return: Boolean
        """
        # If it is elite proxy, then its ip should appear in origin field
        # TODO to be confirm
        origin = result.get('origin').split(', ')
        return proxy in origin

    async def test_single_proxy(self, proxy, timeout=7.0):
        """
        测试单个代理

        :param timeout: 测试代理的最大等待时长，默认为7秒
        :param proxy: 需要测试的代理
        """
        async with aiohttp.ClientSession() as session:
            if isinstance(proxy, bytes):
                proxy = proxy.decode('utf-8')
            real_proxy = proxy.split('__')[0]
            if real_proxy.startswith('https'):
                return
            try:
                async with session.get(TEST_URL, proxy=real_proxy, timeout=timeout) as response:
                    if response.status == 200:
                        self.logger.info(f'Congrats!!!!!!!!!!! {proxy} is still alive!')
                        json_result = await response.json()
                        if self.check_anonymity(proxy, json_result):
                            self.redis.set_max_score(proxy)
                    else:
                        self.redis.degrade_proxy(proxy)
            except Exception as e:
                self.redis.degrade_proxy(proxy)
                self.logger.info(f'Life sucks! {proxy} failed to pass the test!')

    def main(self, sleep_time=5):
        """
        Start batch testing...
        :param sleep_time: wait sleep_time before next round of batch testing
        """
        try:
            self.redis.release_lock()
        except:
            self.logger.info('can not release lock')
        if self.redis.acquire_lock():
            count = self.redis.get_proxy_count()
            for i in range(0, count, BATCH_TEST_SIZE):
                self.logger.info('Start testing proxies...{start + 1} to {stop}')
                start = i
                stop = min(i + BATCH_TEST_SIZE, count)
                try:
                    loop = asyncio.get_event_loop()
                    test_proxies = self.redis.get_batch(start, stop)
                    tasks = [self.test_single_proxy(proxy) for proxy in test_proxies]
                    loop.run_until_complete(asyncio.wait(tasks))
                    time.sleep(sleep_time)
                except Exception as e:
                    self.logger.error(f'测试第 {start + 1}-{stop}个代理出错')
            self.redis.release_lock()


if __name__ == "__main__":
    t = Tester()
    handler = logging.StreamHandler(sys.stdout)
    t.logger.setLevel(logging.DEBUG)
    t.logger.addHandler(handler)
    t.main()
