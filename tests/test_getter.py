import sys
import unittest
import logging
from tests.base import test_rc
from proxypool.getter import Getter
from proxypool.base import Proxy

logger = logging.getLogger()
logger.level = logging.DEBUG


class TestGetter(unittest.TestCase):
    """
    Test Getter
    """

    getter = Getter()
    stream_handler = logging.StreamHandler(sys.stdout)

    def test_collect_and_store(self):
        logger.addHandler(self.stream_handler)
        self.getter.collect()
        count = len(self.getter.proxy_list)
        logger.debug(f'collected {count} proxies')

        for i in self.getter.proxy_list:
            logger.debug(i)
        self.assertGreater(count, 0)

        self.getter.redis = test_rc
        self.getter.redis._clear_key_for_test('test')
        saved = self.getter.store(redis_key='test')
        self.assertEqual(count, saved)

    def teardown(self):
        try:
            self.getter.redis._clear_key_for_test('test')
        except:
            logger.debug('Teardown failed.')
