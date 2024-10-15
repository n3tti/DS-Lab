import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import CloseSpider
from urllib.parse import urljoin

class AdminChSpider(scrapy.Spider):
    name = 'admin_ch3'
    allowed_domains = ['admin.ch']
    start_urls = ['https://www.admin.ch/']
    
    def __init__(self, max_depth=5, *args, **kwargs):
        super(AdminChSpider, self).__init__(*args, **kwargs)
        self.max_depth = int(max_depth)

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, meta={'depth': 0, 'parent_url': 'start_url'})

    def parse(self, response):
        current_depth = response.meta['depth']
        self.logger.info(f'Crawling page at depth {current_depth}: {response.url}')

        # Extract metadata
        metadata = {
            'url': response.url,
            'parent_url': response.meta.get('parent_url', 'unknown'),
            'depth': current_depth,
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
        }

        # Check if we've reached the maximum depth
        if current_depth >= self.max_depth:
            self.logger.info(f'Reached maximum depth of {self.max_depth} at {response.url}')
            return

        # Extract all links on the page
        le = LinkExtractor(allow_domains=self.allowed_domains)
        for link in le.extract_links(response):
            yield scrapy.Request(link.url, callback=self.parse, 
                                 meta={'depth': current_depth + 1, 'parent_url': response.url})