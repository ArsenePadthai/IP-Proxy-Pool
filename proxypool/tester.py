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

    async def test_single_proxy(self, proxy, timeout=5.0):
        """
        测试单个代理

        :param timeout: 测试代理的最大等待时长，默认为5秒
        :param proxy: 需要测试的代理
        """
        async with aiohttp.ClientSession() as session:
            if isinstance(proxy, bytes):
                proxy = proxy.decode('utf-8')
            real_proxy = 'http://' + proxy
            try:
                async with session.get(TEST_URL, proxy=real_proxy, timeout=timeout) as response:
                    if response.status == 200:
                        js = await response.json()
                        origin = js.get('origin').split(', ')
                        # 判断该代理是否为高匿代理
                        # 若为高匿代理会返回两个相同的代理ip
                        if len(origin) == 2 and proxy in origin:
                            self.redis.set_max_score(proxy)
                        else:
                            # 若不是，代理扣除最大分值
                            self.redis.degrade_proxy(proxy, MAX_SCORE)
                    else:
                        self.redis.degrade_proxy(proxy)
            except Exception as e:
                self.redis.degrade_proxy(proxy)
                self.logger.exception(str(e.args))

    def run(self, sleep_time=5):
        """
        测试主函数

        :param sleep_time: 批测试间隔时间，默认为5秒
        """
        # 检查获取器运行状态，若在运行中，则测试器不运行
        getter_flag = self.redis.redis.get('getter:status')

        if getter_flag == 'work':
            return
        self.logger.info('开始测试代理')
        try:
            count = self.redis.get_proxy_count()
            self.logger.info('当前剩余: %d个代理', count)
            for i in range(0, count, BATCH_TEST_SIZE):
                start = i
                stop = min(i + BATCH_TEST_SIZE, count)
                self.logger.info('正在测试第 %d-%d个代理', start + 1, stop)
                test_proxies = self.redis.get_batch(start, stop)
                loop = asyncio.get_event_loop()
                tasks = [self.test_single_proxy(proxy) for proxy in test_proxies]
                loop.run_until_complete(asyncio.wait(tasks))
                time.sleep(sleep_time)
        except Exception as e:
            self.logger.exception(str(e.args))
