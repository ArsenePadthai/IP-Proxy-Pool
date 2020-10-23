import unittest
import re
from proxypool.crawler import Crawler


# TODO: Use decorator to refactor the code
class CrawlerTest(unittest.TestCase):
    """
    Check if can successfully crawl the ip
    """

    crawler = Crawler()

    @staticmethod
    def get_number_of_proxies(proxies):
        """
        统计生成器中有效代理的数量

        :param proxies: 生成器
        :return: 代理数量
        """
        count = 0
        try:
            p = next(proxies)
            while p:
                if re.match(r'\d+\.\d+\.\d+\.\d+:\d+', p):
                    count += 1
                    break
                p = next(proxies)
            return count
        except StopIteration:
            return count

    def test_crawl_freeproxylist(self):
        proxies = [p for p in self.crawler.crawl_free_proxy_list_net()]
        self.assertGreater(len(proxies), 0)



if __name__ == '__main__':
    unittest.main()
