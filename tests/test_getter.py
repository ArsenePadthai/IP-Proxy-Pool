import sys
import unittest
from proxypool.getter import Getter
from proxypool.base import Proxy


class TestGetter(unittest.TestCase):
    """
    Test Getter
    """

    getter = Getter()

    def test_collect(self):
        proxy_list = self.getter.collect()
        for i in proxy_list:
            print(i)
        self.assertGreater(len(proxy_list), 0)

if __name__ == '__main__':
    unittest.main()
