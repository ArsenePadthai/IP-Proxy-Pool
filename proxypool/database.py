import logging

from random import choice
import redis

from proxypool.error import PoolEmptyError
from proxypool.settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_KEY, LOCK_KEY
from proxypool.settings import MAX_SCORE, MIN_SCORE, INITIAL_SCORE, DECREASE_SCORE, POOL_UPPER_THRESHOLD


class RedisClient:
    """
    A customized redis client class.
    Redis客户端类，用于连接数据库对数据进行增删查改等操作
    """

    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        """
        初始化

        :param host: Redis 地址
        :param port: Redis 端口
        :param password: Redis密码
        """
        self.redis = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)
        self.logger = logging.getLogger('main.redis')
        self.pipe = self.redis.pipeline(transaction=True)
        self.size = POOL_UPPER_THRESHOLD

    def is_over_threshold(self):
        return self.get_proxy_count() >= self.size


    def add_proxies(self, proxies, score=INITIAL_SCORE, key=REDIS_KEY):
        """
        Add bulk proxies to the redis pipeline, setting score of each proxy to initial score. But not to update scores of existing proxies.
        :param proxies: 代理
        :param score: 分数
        :param key: 键名
        :return: 存储代理数量
        """
        for proxy in proxies:
            self.pipe.zadd(key, {proxy.__str__(): score}, nx=True)
        saved = sum(self.pipe.execute())
        return saved

    def random_get_proxy(self):
        """
        随机获取有效代理，首先尝试获取最高分数代理，如果不存在，按照排名获取，否则异常

        :return: 随机代理
        """
        # 获取分数大于等于100的代理
        result = self.redis.zrangebyscore(REDIS_KEY, MAX_SCORE, '+inf')
        if len(result):
            return choice(result)
        else:
            # 获无符合条件的代理，则获取分数大于等于初始分数的代理
            result = self.redis.zrevrangebyscore(REDIS_KEY, '+inf', INITIAL_SCORE)
            if len(result):
                return choice(result)
            else:
                raise PoolEmptyError

    def degrade_proxy(self, proxy, count=DECREASE_SCORE):
        """
        代理值减分，小于最小值则删除

        :param proxy: 代理
        :param count: 要扣的分
        :return: 修改后的代理分数
        """
        score = self.redis.zscore(REDIS_KEY, proxy)
        if score and score > MIN_SCORE:
            return self.redis.zincrby(REDIS_KEY, count, proxy)
        else:
            return self.redis.zrem(REDIS_KEY, proxy)

    def exists(self, proxy):
        """
        判断数据库中是否存在某代理

        :param proxy: 代理
        :return: 是否存在，
        """
        return not (self.redis.zscore(REDIS_KEY, proxy) is None)

    def set_max_score(self, proxy, rd_key=REDIS_KEY):
        """
        Add/update proxy score with maximum score.
        :param proxy: 
        :return: 
        """
        return self.redis.zadd(rd_key, {proxy: MAX_SCORE})

    def get_proxy_count(self):
        """
        :return: count result of all proxies.
        """
        return self.redis.zcard(REDIS_KEY)

    def get_all_ascending(self):
        """
        获取全部代理，按分数升序

        :return: 全部代理列表
        """
        return self.redis.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)

    def get_batch(self, start, stop):
        """
        从数据库中批量获取代理

        :param start: 开始索引
        :param stop: 结束索引
        :return: 代理列表
        """
        return self.redis.zrevrange(REDIS_KEY, start, stop - 1)

    def get_all_available(self):
        """
        从数据库中获取所有可用代理

        :return: 代理列表
        """
        return self.redis.zrangebyscore(REDIS_KEY, MAX_SCORE, '+inf')

    def acquire_lock(self, key=LOCK_KEY):
        """
        从redis获取锁

        :param key: 锁的键名
        :return: 成功获取返回True，否则返回False
        """
        return self.redis.get(key) == '1' and self.redis.decr(key) == 0

    def release_lock(self, key=LOCK_KEY):
        """
        释放锁

        :param key: 锁的键名
        :return: 成功释放返回True，否则返回False
        """
        return self.redis.get(key) == '0' and self.redis.incr(key) == 1


if __name__ == "__main__":
    r = RedisClient(host='127.0.0.1')
    for i in r.get_batch(0, 20):
        print(i)

