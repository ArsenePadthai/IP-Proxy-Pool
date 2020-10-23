from unittest import TestCase

from proxypool.database import RedisClient


class TestRedisClient(TestCase):
    def setUp(self):
        self.rc = RedisClient(host='127.0.0.1', port=6379, password='wsxcv123')

    def test_add_proxies(self):
        test_data = [str(i) for i in range(100)]
        self.rc.pipe.delete('test')
        self.rc.pipe.execute()
        ret = self.rc.add_proxies(test_data, key='test')
        self.assertEqual(len(test_data), ret)

    def test_set_max_score(self):
        self.rc.redis.delete('test')
        self.rc.set_max_score('12345', rd_key='test')
        self.assertEqual(100, self.rc.redis.zscore(name='test', value='12345'))

