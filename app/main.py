from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from app.adminch_crawler.spiders.crawling_spider import CrawlingSpider
import newrelic.agent
from app.logs import logger
import logging
import time
import app.config
import sys



newrelic.agent.initialize('newrelic.ini')
newrelic.agent.register_application()


if __name__ == "__main__":
    # logging.getLogger('scrapy').propagate = False 
    logger.info("Application is running", iteration=1, status="OK")

    process = CrawlerProcess(get_project_settings())
    process.crawl(CrawlingSpider)
    process.start() 

# logging_loger = logging.getLogger()

# def main():
#     count = 0
#     while True:  # Infinite loop
#         count += 1
#         logger.debug("Application is running", iteration=count, status="OK")
#         logger.info("Application is running", iteration=count, status="OK")
#         logging_loger.info("logging: Application is running")
#         try:
#             1 / 0
#         except Exception as e:
#             logger.error(e)
#         time.sleep(2)  # Wait 2 seconds before logging the next message


# if __name__ == "__main__":
#     main()