# from scrapy.utils.log import LogFormatter
from scrapy.logformatter import LogFormatter
import scrapy
from app.logs import logger

class CustomLogFormatter(LogFormatter):
    def format(self, record):
        print("IM FORMATTER")
        # You can integrate structlog here or format the record as needed
        logger.log(record.levelno, record.getMessage())
        return super().format(record)


class QuietLogFormatter(scrapy.logformatter.LogFormatter):
    def scraped(self, item, response, spider):
        print("IM FORMATTER2")
        return (
            super().scraped(item, response, spider)
            if spider.settings.getbool("LOG_SCRAPED_ITEMS")
            else None
        )