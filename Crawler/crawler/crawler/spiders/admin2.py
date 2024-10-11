import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import CloseSpider
from urllib.parse import urljoin

class AdminChSpider(scrapy.Spider):
    name = 'admin_ch'
    allowed_domains = ['admin.ch']
    start_urls = ['https://www.admin.ch/']
    
    def __init__(self, max_pages=1000, *args, **kwargs):
        super(AdminChSpider, self).__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.pages_crawled = 0

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, meta={'parent_url': 'start_url'})

    def parse(self, response):
        self.pages_crawled += 1
        self.logger.info(f'Crawling page {self.pages_crawled}: {response.url}')

        # Extract metadata
        metadata = {
            'url': response.url,
            'parent_url': response.meta.get('parent_url', 'unknown'),
            'title': response.css('title::text').get(),
            'description': response.css('meta[name="description"]::attr(content)').get(),
            'keywords': response.css('meta[name="keywords"]::attr(content)').get(),
            'last_modified': response.headers.get('Last-Modified', b'').decode(),
            'content_type': response.headers.get('Content-Type', b'').decode(),
        }

        # Extract all paragraph text
        content = ' '.join(response.css('p::text').getall())

        # Extract PDF links
        pdf_links = []
        for href in response.css('a::attr(href)').getall():
            full_url = urljoin(response.url, href)
            if full_url.lower().endswith('.pdf'):
                pdf_links.append(full_url)

        yield {
            'metadata': metadata,
            'content': content,
            'pdf_links': pdf_links,
            'pages_crawled': self.pages_crawled,
        }

        # Check if we've reached the maximum number of pages
        if self.pages_crawled >= self.max_pages:
            raise CloseSpider(f'Reached maximum number of pages: {self.max_pages}')

        # Extract all links on the page
        le = LinkExtractor(allow_domains=self.allowed_domains)
        for link in le.extract_links(response):
            yield scrapy.Request(link.url, callback=self.parse, meta={'parent_url': response.url})
