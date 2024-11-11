from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import logging

from app.adminch_crawler.spiders.crawling_spider import CrawlingSpider

logger = logging.getLogger(__name__.split(".")[-1])

if __name__ == "__main__":
    logger.info("Starting spider")
    process = CrawlerProcess(get_project_settings())
    process.crawl(CrawlingSpider)
    process.start()
