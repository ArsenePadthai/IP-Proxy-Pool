from unittest import TestCase

from proxypool.database import RedisClient


class TestRedisClient(TestCase):
    def test_add_proxies(self):
        redis = RedisClient(host='127.0.0.1', port=6379, password='Wsxcv135')
        test_data = [str(i) for i in range(100)]
        redis.pipe.delete('test')
        redis.pipe.execute()
        ret = redis.add_proxies(test_data, key='test')
        self.assertEqual(len(test_data), ret)
