from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from crawler.items import PageItem
from urllib.parse import urljoin

import pdb

class CrawlingSpider(CrawlSpider):
    name = "mycrawler2"
    allowed_domains = ["admin.ch"]
    start_urls = ["https://www.admin.ch/"]
    
    rules = (
        Rule(
            LinkExtractor(
                allow_domains=allowed_domains,
                allow=r".*\.html?$|.*/$|.*(?<!\.)\w+$",
            ),
            callback='parse_item',
            follow=True
        ),
    )

    def parse_item(self, response):

        item = PageItem()

        # about webrequest
        item["id"] = None
        item["status"] = response.status
        item["depth"] = response.meta["depth"]
        item["url"] = response.url

        # items that are obtained further below
        item["child_urls"] = {}
        item["cousin_urls"] = {}
        item["pdf_links"] = []

        # metadata
        item["content_type"] = response.headers.get('Content-Type', b'').decode('utf-8') if response.headers.get('Content-Type') else None
        item["content_length"] = int(response.headers.get('Content-Length').decode('utf-8')) if response.headers.get('Content-Length') else None
        item["content_encoding"] = response.headers.get('Content-Encoding', b'').decode('utf-8') if response.headers.get('Content-Encoding') else None
        item["last_modified"] = response.headers.get("Last-Modified").decode('utf-8') if response.headers.get('Last-Modified') else None
        item["date"] = response.headers.get('Date').decode('utf-8') if response.headers.get('Date') else None
        item["title"] = response.headers.get('Title').decode('utf-8') if response.headers.get('Title') else None
        item['description'] = response.css('meta[name="description"]::attr(content)').get()
        item['keywords'] = response.css('meta[name="keywords"]::attr(content)').get()

        item["content_body"] = response.body

        item["content"] = ' '.join(response.css('p::text').getall())


        alternate_links = response.xpath('//link[@rel="alternate"]')
        languages_dict = {}
        for link in alternate_links:
            lang = link.xpath('@lang').get()
            href = link.xpath('@href').get()
            if lang and href:
                languages_dict[lang] = response.urljoin(href)
        item['cousin_urls'] = languages_dict

        for link in response.css('a::attr(href)').getall():
            full_url = urljoin(response.url, link)

            # get child and cousin urls
            if link not in item["cousin_urls"].keys() and link != response.url:
                item["child_urls"][full_url] = None

            # get pdf links of this page
            if full_url.lower().endswith('.pdf'):
                item["pdf_links"].append(full_url)

        yield item
            

   