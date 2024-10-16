from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from crawler.items import PageItem
import pdb

class CrawlingSpider(CrawlSpider):
    name = "mycrawler"
    allowed_domains = ["admin.ch"]
    start_urls = ["https://www.admin.ch/"]

    custom_settings = {
    'DEPTH_LIMIT': 4,  
    'DOWNLOAD_DELAY': 1.0, 
    #'CONCURRENT_REQUESTS': 16, 
    #'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429]
    'LOG_LEVEL': 'ERROR',  # Only log errors
    'LOG_FILE': 'crawler.log',  # Save logs to this file
    "LOG_FILE_APPEND" : False,
    'LOG_STDOUT': False  # Don't print log messages to stdout
    }
    

    rules = (
        Rule(LinkExtractor(allow=allowed_domains, deny=(
            r'\.docx$', r'\.xlsx$', r'\.pptx$', r'\.zip$', r'\.tar$', r'\.gz$', r'\.jpg$', 
            r'\.jpeg$', r'\.gif$', r'\.svg$', r'\.mp3$', r'\.mp4$', r'\.avi$', r'\.mov$', 
            r'\.wmv$', r'\.txt$', r'\.json$', r'\.csv$', r'\.xml$', r'^mailto:', r'\.js$', 
            r'\.css$', r'\.exe$', r'\.bin$'
        )), callback='parse_item', follow=True, process_request='add_parent_url'),
    )


    def parse_item(self, response):
        item = PageItem()
        item["id"] = None
        item["status"] = response.status
        item["depth"] = response.meta["depth"]
        item["url"] = response.url 
        item["child_urls"] = {}
        item["cousin_urls"] = {}

        item["content_type"] = response.headers.get('Content-Type', b'').decode('utf-8') if response.headers.get('Content-Type') else None
        item["content_length"] = int(response.headers.get('Content-Length').decode('utf-8')) if response.headers.get('Content-Length') else None
        item["content_encoding"] = response.headers.get('Content-Encoding', b'').decode('utf-8') if response.headers.get('Content-Encoding') else None
        item["content_body"] = response.body
        item["last_modified"] = response.headers.get("Last-Modified").decode('utf-8') if response.headers.get('Last-Modified') else None
        item["date"] = response.headers.get('Date').decode('utf-8') if response.headers.get('Date') else None
        item["lang"] = response.xpath("//html/@lang").get()
        alternate_links = response.xpath('//link[@rel="alternate"]')
        languages_dict = {}
        for link in alternate_links:
            lang = link.xpath('@lang').get()
            href = link.xpath('@href').get()
            if lang and href:
                languages_dict[lang] = response.urljoin(href)
        item['cousin_urls'] = languages_dict

            