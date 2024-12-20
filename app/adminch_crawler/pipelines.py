# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import Spider
from scrapy.exceptions import DropItem
from simhash import Simhash

from app.logs import logger
from app.repository.db import db
from app.repository.models import PageStatusEnum, ScrapedPage


class DiscoveredStoragePipeline:
    def process_item(self, scraped_page: ScrapedPage, spider: Spider) -> ScrapedPage:
        existing_page = db.get_scraped_page(url=scraped_page.url)

        if existing_page is None:
            created_page = db.create_scraped_page(scraped_page)
            return created_page

        elif existing_page.status == PageStatusEnum.COMPLETED:
            raise DropItem(f"url: '{scraped_page.url}' is already COMPLETED.")
        else:
            db.update_scraped_page_status(scraped_page_id=scraped_page.id, status=PageStatusEnum.REVISITED)

            scraped_page.id = existing_page.id  # set id to the scraped object
            return scraped_page


class FilterURLPipeline:
    def __init__(self):
        self.allowed_content_type = ["text/html"]

    def process_item(self, scraped_page: ScrapedPage, spider: Spider) -> ScrapedPage:

        logger.info(f"Processing url: {scraped_page}")

        if scraped_page.response_status_code != 200:
            db.update_scraped_page_status(scraped_page.id, PageStatusEnum.FAILED)
            raise DropItem(f"HTTP Status: {scraped_page.response_status_code}: {scraped_page}.")
        elif scraped_page.response_content_type is None:
            db.update_scraped_page_status(scraped_page.id, PageStatusEnum.FAILED)
            raise DropItem("Content_type is None.")
        elif not scraped_page.response_content_type.split(";")[0] in self.allowed_content_type:
            db.update_scraped_page_status(scraped_page.id, PageStatusEnum.FAILED)
            raise DropItem(f"Content type \"{scraped_page.response_content_type.split(';')[0]}\" is not allowed.")

        return scraped_page


class CompletedStoragePipeline:
    def process_item(self, scraped_page: ScrapedPage, spider: Spider) -> ScrapedPage:
        db.update_scraped_page_status(scraped_page_id=scraped_page.id, status=PageStatusEnum.COMPLETED)

        return scraped_page
