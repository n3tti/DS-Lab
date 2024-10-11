import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import CloseSpider
from urllib.parse import urljoin, urlparse, parse_qs
import hashlib

class AdminChAdvancedSpider(scrapy.Spider):
    name = 'admin_ch_advanced'
    allowed_domains = ['admin.ch']
    start_urls = ['https://www.admin.ch/de']
    
    def __init__(self, max_pages=10, *args, **kwargs):
        super(AdminChAdvancedSpider, self).__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.pages_crawled = 0
        self.url_data = {}  # Store data for each URL

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, meta={'parent_urls': set()})

    def get_url_id(self, url):
        # Generate a unique ID for the URL
        return hashlib.md5(url.encode()).hexdigest()

    def get_language(self, url):
        # Extract language from URL or content
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        return query_params.get('lang', ['unknown'])[0]

    def get_base_url(self, url):
        # Get base URL without language parameter
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        query_params.pop('lang', None)
        new_query = '&'.join(f"{k}={v[0]}" for k, v in query_params.items())
        return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{new_query}"

    def parse(self, response):
        url_id = self.get_url_id(response.url)
        language = self.get_language(response.url)
        base_url = self.get_base_url(response.url)
        parent_urls = response.meta.get('parent_urls', set())

        if url_id not in self.url_data:
            self.pages_crawled += 1
            self.url_data[url_id] = {
                'url': response.url,
                'base_url': base_url,
                'language': language,
                'parent_urls': parent_urls,
                'child_urls': set()
            }
        else:
            # Update parent URLs if this page was reached through a new path
            self.url_data[url_id]['parent_urls'].update(parent_urls)

        # Update child URLs for all parent URLs
        for parent_url in parent_urls:
            parent_id = self.get_url_id(parent_url)
            if parent_id in self.url_data:
                self.url_data[parent_id]['child_urls'].add(response.url)

        # Extract metadata
        metadata = {
            'url_id': url_id,
            'url': response.url,
            'base_url': base_url,
            'language': language,
            'parent_urls': list(parent_urls),
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
            new_meta = response.meta.copy()
            new_meta['parent_urls'] = parent_urls.union({response.url})
            yield scrapy.Request(link.url, callback=self.parse, meta=new_meta)

    def closed(self, reason):
        # When the spider closes, yield the final URL data
        for url_id, data in self.url_data.items():
            yield {
                'url_id': url_id,
                'url': data['url'],
                'base_url': data['base_url'],
                'language': data['language'],
                'parent_urls': list(data['parent_urls']),
                'child_urls': list(data['child_urls'])
            }