# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import random

from fake_useragent import UserAgent

# useful for handling different item types with a single interface
from scrapy import signals


class RotateUserAgentMiddleware:

    def process_request(self, request, spider):
        ua = UserAgent()
        agent = ua.random
        # spider.logger.info("User-Agent: %s" % agent)
        request.headers.setdefault("User-Agent", agent)
