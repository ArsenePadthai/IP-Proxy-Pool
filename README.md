# IP-Proxy-Pool

I forked this repo from fgksgf/IP-Proxy-Pool. I use this project to prepare free proxies for my other scrapy projects. I didn't change main structure of the project. I think the author did a very good job. The project is simple enough but can do the right things. But I do adapt some detail implementations to server for my own purpose. 

The pool contains three sub-modules: the proxy getter, the proxy tester, and the interface module.

+ The proxy getter is responsible for regularly crawling free and high-anonymous proxies from several websites and storing them in the redis. 

+ The proxy tester regularly checks the availability of the proxies in redis, that is, using the proxy to request a specified test link. And each proxy has a score that indicates its availability.

+ The interface module is responsible for providing APIs for external services, such as quering the number of proxies in the pool or randomly obtaining an available proxy.

**It is highly recommended that deploying this pool on a server as a independent node.**

## Usage

```bash
$ git clone https://github.com/ArsenePadthai/IP-Proxy-Pool.git
$ cd IP-Proxy-Pool/

# set your own password of redis
$ cp redis.conf.example redis.conf
$ vim redis.conf
$ cp proxypool/settings.py.example proxypool/settings.py
$ vim proxypool/settings.py

# set your absolute path of IP-Proxy-Pool/ on line 17
$ cp docker-compose.yml.example docker-compose.yml
$ vim docker-compose.yml

$ docker-compose up -d
```

Then you can use `docker logs <container id>` to check logs. For checking proxies, you can connect redis at 127.0.0.1:6379 via redis GUI tools.

## Run unittest

Simple unittest can be runned outside of docker.
```bash
virtualenv -p python3 venv
source venv/bin/activate
```

```bash
python -m unittest tests.test_crawler
python -m unittest tests.test_database
python -m unittest tests.test_getter
```

You may need to change the redis password in test_database.py to pass the tests.

### API

You can access `127.0.0.1:5000` to get these services:

+   `/random`: get a random proxy in the pool.
+   `/batch`: get all currently available proxies.
+   `/count`: get the number of proxies.