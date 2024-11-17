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

def wait_for_newrelic_startup(timeout=15):
    start_time = time.time()
    while not newrelic.agent.application().active:
        if time.time() - start_time > timeout:
            raise TimeoutError("New Relic did not start in the expected time.")
        time.sleep(0.5)

if not DEBUG:
    newrelic.agent.initialize('newrelic.ini')
    newrelic.agent.register_application()

    wait_for_newrelic_startup()

if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl(CrawlingSpider)
    process.start() 
