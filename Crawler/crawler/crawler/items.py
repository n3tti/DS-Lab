# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PageItem(scrapy.Item):

    id = scrapy.Field()
    status = scrapy.Field()
    depth = scrapy.Field()
    url = scrapy.Field()
    cousin_urls = scrapy.Field()
    child_urls = scrapy.Field()
    content_type = scrapy.Field()
    content_length = scrapy.Field()
    content_encoding = scrapy.Field()
    content_body = scrapy.Field()
    last_modified = scrapy.Field()
    date = scrapy.Field()
    
    content = scrapy.Field()
    title = scrapy.Field()
    pdf_links = scrapy.Field()
