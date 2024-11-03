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
    content_type = scrapy.Field()
    content_length = scrapy.Field()
    content_encoding = scrapy.Field()
    last_modified = scrapy.Field()
    date = scrapy.Field()
    lang = scrapy.Field()
    title = scrapy.Field()

    cousin_urls = scrapy.Field()
    child_urls = scrapy.Field()

    content_body = scrapy.Field()
    hash = scrapy.Field()
    content = scrapy.Field()

    pdf_links = scrapy.Field()
    embedded_images = scrapy.Field()
    img_alt = scrapy.Field()

    description = scrapy.Field()
    keywords = scrapy.Field()

    error = scrapy.Field()

    def __repr__(self):
        return repr(
            {
                "id": self["id"],
                "status": self["status"],
                "depth": self["depth"],
                "url": self["url"],
                "content_type": self["content_type"],
            }
        )
