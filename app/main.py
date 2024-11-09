# main.py
import scrapy
from scrapy.crawler import CrawlerProcess
from app.adminch_crawler.spiders.crawling_spider import CrawlingSpider
from scrapy.utils.project import get_project_settings


if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl(CrawlingSpider)
    process.start()



# from app.repository.db import db


# if __name__ == '__main__':
#     db.create_user(name="Alice", email="alice@example.com")
#     user = db.get_user(name="Alice")
    
#     print(user)
#     print()