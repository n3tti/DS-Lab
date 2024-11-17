from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from app.adminch_crawler.spiders.crawling_spider import CrawlingSpider
import newrelic.agent
from app.logs import logger
import logging
import time
import app.config
from app.config import DEBUG
import sys


if not DEBUG:
    newrelic.agent.initialize('newrelic.ini')
    newrelic.agent.register_application()


if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl(CrawlingSpider)
    process.start() 
