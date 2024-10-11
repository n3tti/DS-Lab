import scrapy
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urljoin, urlparse
from collections import defaultdict

class MultiLanguageSpider(scrapy.Spider):
    name = 'admin_ch5'
    allowed_domains = ['admin.ch']  # Change this to your target domain
    start_urls = ['https://www.admin.ch/']  # Change this to your starting URL

    custom_settings = {
        'LOG_LEVEL': 'INFO',
        'LOG_FILE': 'multi_language_spider.log',
        'LOG_STDOUT': False
    }

    def __init__(self, max_depth=5, *args, **kwargs):
        super(MultiLanguageSpider, self).__init__(*args, **kwargs)
        self.max_depth = int(max_depth)
        self.parent_urls = defaultdict(set)
        self.url_counter = 0
        self.equivalent_pages = defaultdict(dict)
        self.current_page_group = None
        self.supported_languages = ['en', 'fr', 'de', 'it']  # Add or remove languages as needed

    def get_language(self, url):
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.split('/')
        if len(path_parts) > 1 and path_parts[1] in self.supported_languages:
            return path_parts[1]
        return 'en'  # Default to 'en' if no language is specified

    def get_url_id(self, url):
        language = self.get_language(url)
        
        # Check if this URL is part of a known group of equivalent pages
        for group_id, urls in self.equivalent_pages.items():
            if url in urls.values():
                self.current_page_group = group_id
                return group_id

        # If not, create a new group
        self.url_counter += 1
        new_group_id = self.url_counter
        self.equivalent_pages[new_group_id] = {language: url}
        self.current_page_group = new_group_id
        return new_group_id

    def add_equivalent_url(self, url, language):
        if self.current_page_group:
            self.equivalent_pages[self.current_page_group][language] = url

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, meta={'depth': 0})

    def parse(self, response):
        current_depth = response.meta['depth']
        current_url = response.url
        current_url_id = self.get_url_id(current_url)
        current_language = self.get_language(current_url)

        self.logger.info(f'Crawling page at depth {current_depth}: {current_url} (ID: {current_url_id}, Language: {current_language})')

        # Extract metadata
        metadata = {
            'url': current_url,
            'url_id': current_url_id,
            'language': current_language,
            'parent_url_ids': list(self.parent_urls[current_url_id]),
            'depth': current_depth,
            'title': response.css('title::text').get(),
            'description': response.css('meta[name="description"]::attr(content)').get(),
            'keywords': response.css('meta[name="keywords"]::attr(content)').get(),
            'last_modified': response.headers.get('Last-Modified', b'').decode(),
            'content_type': response.headers.get('Content-Type', b'').decode(),
            'equivalent_urls': self.equivalent_pages[current_url_id]
        }

        # Extract all paragraph text
        content = ' '.join(response.css('p::text').getall())

        # Extract PDF links
        pdf_links = []
        for href in response.css('a::attr(href)').getall():
            full_url = urljoin(response.url, href)
            if full_url.lower().endswith('.pdf'):
                pdf_links.append(full_url)

        # Look for language switcher links
        for lang in self.supported_languages:
            lang_url = response.css(f'a[hreflang="{lang}"]::attr(href)').get()
            if lang_url:
                full_lang_url = response.urljoin(lang_url)
                self.add_equivalent_url(full_lang_url, lang)

        yield {
            'metadata': metadata,
            'content': content,
            'pdf_links': pdf_links
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

# To run the spider, use:
# scrapy crawl admin_ch5 -a max_depth=2 -O output5.json