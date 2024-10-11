
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class CrawlingSpider(CrawlSpider):
    name = "mycrawler"
    allowed_domains = ["admin.ch"]
    start_urls = ["https://www.admin.ch/"]

    custom_settings = {
    'DEPTH_LIMIT': 4,  
    #'DOWNLOAD_DELAY': 1.0,  
    #'CONCURRENT_REQUESTS': 16, 
    'LOG_LEVEL': 'WARNING', 
    #'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429]
    }
    
    rules = (
        Rule(LinkExtractor(allow=(), deny=(r'\.docx$', r'\.xlsx$', r'^mailto:', r'\.jpg$', r'\.png$')), callback='parse_item', follow=True),
    )


    def parse_item(self, response):
        parent_url = response.url

        for link in response.css('a::attr(href)').getall(): # url will be any type of page
            child_url = response.urljoin(link)
            yield {'parent_url': parent_url, 'child_url' : child_url}