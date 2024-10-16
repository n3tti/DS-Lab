import scrapy
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urljoin
from collections import defaultdict
import logging
from scrapy.utils.log import configure_logging

class AdminChSpider(scrapy.Spider):
    name = 'admin_ch4'
    allowed_domains = ['admin.ch']
    start_urls = ['https://www.admin.ch/']

    custom_settings = {
        'LOG_LEVEL': 'ERROR',  # Only log errors
        'LOG_FILE': 'crawler.log',  # Save logs to this file
        'LOG_STDOUT': False  # Don't print log messages to stdout
    }
    
    def __init__(self, max_depth=5, *args, **kwargs):
        super(AdminChSpider, self).__init__(*args, **kwargs)
        self.max_depth = int(max_depth)
        self.parent_urls = defaultdict(set)
        self.url_to_id = {}
        self.id_to_url = {}
        self.url_counter = 0

        configure_logging(self.custom_settings)
      

    def get_url_id(self, url):
        if url not in self.url_to_id:
            self.url_counter += 1
            self.url_to_id[url] = self.url_counter
            self.id_to_url[self.url_counter] = url
        return self.url_to_id[url]
        

    def start_requests(self):
        for url in self.start_urls:
            url_id = self.get_url_id(url)
            self.parent_urls[url_id].add('start_url')
            yield scrapy.Request(url, callback=self.parse, meta={'depth': 0})

    def parse(self, response):
        current_depth = response.meta['depth']
        current_url = response.url
        current_url_id = self.get_url_id(current_url)
        self.logger.info(f'Crawling page at depth {current_depth}: {current_url} (ID: {current_url_id})')

        # Extract metadata
        metadata = {
            'url': current_url,
            'url_id': current_url_id,
            'parent_url_ids': list(self.parent_urls[current_url_id]),
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
            self.logger.info(f'Reached maximum depth of {self.max_depth} at {current_url}')
            return

        # Extract all links on the page
        le = LinkExtractor(allow_domains=self.allowed_domains)
        for link in le.extract_links(response):
            link_url_id = self.get_url_id(link.url)
            self.parent_urls[link_url_id].add(current_url_id)
            yield scrapy.Request(link.url, callback=self.parse, 
                                 meta={'depth': current_depth + 1})
