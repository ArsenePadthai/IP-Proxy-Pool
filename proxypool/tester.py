import sys
import asyncio
import logging

import aiohttp
import time

from proxypool.database import RedisClient
from proxypool.settings import *


class Tester:
    def __init__(self):
        self.redis = RedisClient()
        self.logger = logging.getLogger('main.tester')

    @staticmethod
    def check_anonymity(proxy_ip, result):
        """
        Check if a specific proxy is anonymous
        :param proxy: ip address of the proxy.
        :param result: result acquired from test url.
        :return: Boolean
        """
        # If it is elite proxy, then its ip should appear in origin field
        # TODO to be confirm
        origin = result.get('origin').split(', ')
        return proxy_ip in origin

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
            # aiohttp does not support https proxy yet
            if real_proxy.startswith('https'):
                return
            ip = real_proxy.split(':')[1][2:]
            try:
                async with session.get(TEST_URL, proxy=real_proxy, timeout=timeout) as response:
                    if response.status == 200:
                        json_result = await response.json()
                        self.logger.debug(ip)
                        if self.check_anonymity(ip, json_result):
                            self.logger.info(f'Congrats!! {proxy} is elite proxy!')
                            self.redis.set_max_score(proxy)
                    else:
                        self.redis.degrade_proxy(proxy)
            except Exception as e:
                self.redis.degrade_proxy(proxy)
                self.logger.info(f'Life sucks! {proxy} failed to pass the test!')
                self.logger.debug(str(e))

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
                start = i
                stop = min(i + BATCH_TEST_SIZE, count)
                self.logger.info(f'Start testing proxies...{start + 1} to {stop}')
                try:
                    loop = asyncio.get_event_loop()
                    test_proxies = self.redis.get_batch(start, stop)
                    tasks = [self.test_single_proxy(proxy) for proxy in test_proxies]
                    loop.run_until_complete(asyncio.wait(tasks))
                    time.sleep(sleep_time)
                except Exception as e:
                    self.logger.error(f'Something went wrong then when we were testing from {start + 1} to {stop}')
                    self.logger.error(str(e))
            self.redis.release_lock()


# if __name__ == "__main__":
#     t = Tester()
#     handler = logging.StreamHandler(sys.stdout)
#     t.logger.setLevel(logging.DEBUG)
#     t.logger.addHandler(handler)
#     t.main()
