import logging, re
from urllib.parse import urljoin, urlparse

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_playwright.page import PageMethod
from scrapy.http import Request

from app.repository.models import ScrapedPage

logger = logging.getLogger(__name__.split(".")[-1])


class CrawlingSpider(CrawlSpider):
    name = "my2crawler"
    allowed_domains = ["admin.ch", "ch.ch"]
    start_urls = [#"https://www.admin.ch/", 
    "https://www.ch.ch/de/steuern-und-finanzen/steuerarten/mehrwertsteuer/#"]

    excluded_subdomains = [
        'https://www.obsan.admin.ch',
        # Add more subdomains to exclude as needed
    ]

    def __init__(self, restart="False", *a, **kw):
        super().__init__(*a, **kw)
        self.is_resuming_var = not (restart.lower() == "true")
        self.excluded_domain_counts = {domain: 0 for domain in self.excluded_subdomains}
        self.setup_excluded_domain_logging()

    custom_settings = {
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.PlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.PlaywrightDownloadHandler"
        },
        'TWISTED_REACTOR': "twisted.internet.asyncio.AsyncioSelectorReactor",
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            "headless": True,
        },
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 30000,
    }

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                url,
                meta=dict(
                    playwright=True,
                    playwright_include_page=True,
                    playwright_page_methods=[
                        PageMethod("setJavaScriptEnabled", True),
                        PageMethod("wait_for_load_state", "networkidle"),
                    ],
                ),
                dont_filter=True
            )

    def setup_excluded_domain_logging(self):
        """Setup specific logging for excluded domains"""
        self.excluded_logger = logging.getLogger(f"{__name__}.excluded_domains")
        log_filename = f"excluded_domains.log"
        fh = logging.FileHandler(log_filename)
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        fh.setFormatter(formatter)
        self.excluded_logger.addHandler(fh)
        self.excluded_logger.setLevel(logging.INFO)

    def should_follow_url(self, url):
        """Check if the URL should be followed based on subdomain rules"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        for excluded in self.excluded_subdomains:
            if domain.endswith(excluded):
                self.excluded_domain_counts[excluded] += 1
                self.excluded_logger.info(f"Excluded URL: {url} (matches {excluded})")
                logger.info(f"Skipping excluded domain: {domain} (matched {excluded})")
                return False
        return True

    rules = (
        Rule(
            LinkExtractor(
                allow_domains=allowed_domains,
                allow=r".*\.html?.*",
                deny=([rf"https?://{re.escape(subdomain)}.*" for subdomain in excluded_subdomains]),
            ),
            callback="parse_item",
            follow=True,
            process_request='process_request'
        ),
    )

    def process_request(self, request, response):
        """Additional URL filtering at request level"""
        if not self.should_follow_url(request.url):
            return None

        # Add Playwright metadata to all requests
        request.meta.update({
            'playwright': True,
            'playwright_include_page': True,
            'playwright_page_methods': [
                PageMethod("wait_for_load_state", "networkidle"),
            ]
        })
        return request

    def is_resuming(self):
        return self.is_resuming_var

    def closed(self, reason):
        """Called when the spider is closed"""
        self.excluded_logger.info("\n=== Final Excluded Domain Statistics ===")
        for domain, count in self.excluded_domain_counts.items():
            self.excluded_logger.info(f"Domain: {domain} - Encountered {count} times")
        logger.info("Spider closed. Check excluded_domains_[timestamp].log for detailed statistics")

    async def parse_item(self, response):
        page = response.meta["playwright_page"]

        try:
            # Wait for content to be fully loaded
            await page.wait_for_load_state("networkidle")

            # Extract content after JavaScript execution
            content = await page.content()

            #####################################################
            cousin_urls_dict = {}
            alternate_links = response.xpath('//link[@rel="alternate"]')
            languages_dict = {}
            for link in alternate_links:
                lang = link.xpath("@lang").get()
                href = link.xpath("@href").get()
                if lang and href:
                    languages_dict[lang] = response.urljoin(href)
            cousin_urls_dict = languages_dict

            #####################################################
            pdf_urls = []
            for link in response.css("a::attr(href)").getall():
                full_url = urljoin(response.url, link)
                if full_url.lower().endswith(".pdf"):
                    pdf_urls.append(full_url)

            #####################################################
            child_urls = []
            for link in response.css("a::attr(href)").getall():
                full_url = urljoin(response.url, link)
                if link not in cousin_urls_dict.keys() and link not in pdf_urls and link != response.url:
                    child_urls.append(full_url)

            #####################################################
            embedded_images, img_alt_dict = self.extract_images(response)

            #####################################################
            content_formatted_with_markdown = self.format_content_with_markdown(response)

            #####################################################
            lang = response.xpath("//html/@lang").get()
            if not lang:
                lang = response.xpath(
                    "//meta[@http-equiv='content-language']/@content | //meta[@property='og:locale']/@content").get()

            #####################################################
            try:
                description = response.css('meta[name="description"]::attr(content)').get()
            except Exception:
                description = None
            try:
                keywords = response.css('meta[name="keywords"]::attr(content)').get()
            except Exception:
                keywords = None

            scraped_page = ScrapedPage(
                url=response.url,
                depth=response.meta["depth"],
                response_status_code=response.status,
                response_text=content,  # Using the JavaScript-rendered content
                response_content_type=response.headers.get("Content-Type"),
                response_content_length=response.headers.get("Content-Length"),
                response_content_encoding=response.headers.get("Content-Encoding"),
                response_last_modified=response.headers.get("Last-Modified"),
                response_date=response.headers.get("Date"),
                response_metadata_lang=lang,
                response_metadata_title=self.get_title(response),
                response_metadata_description=description,
                response_metadata_keywords=keywords,
                response_metadata_content_hash=None,
            )
            scraped_page.cousin_urls_dict = cousin_urls_dict
            scraped_page.pdf_urls = pdf_urls
            scraped_page.child_urls = child_urls
            scraped_page.embedded_images = embedded_images
            scraped_page.img_alt_dict = img_alt_dict
            scraped_page.content_formatted_with_markdown = content_formatted_with_markdown

            pdb.set_trace()

            yield scraped_page

        finally:
            await page.close()

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
        logger.error(f"Request failed: {failure.value}")

    def extract_images(self, response):
        """Extract embedded images from content"""
        images = []
        img_alt_dict = {}
        for img in response.css("img"):
            src = img.attrib.get("src")
            if src:
                full_url = urljoin(response.url, src)
                alt = img.attrib.get("alt", "")
                images.append(full_url)
                img_alt_dict[full_url] = alt
        return images, img_alt_dict

    def get_title(self, response):
        """Extract title from multiple possible sources"""
        title = response.headers.get("Title", b"").decode("utf-8") or response.css("title::text").get() or response.css(
            "h1::text").get() or ""
        return title.strip()

    def format_content_with_markdown(self, response):
        """Format content with markdown, preserving the original order of elements"""
        content_parts = []

        for element in response.css("h1, h2, h3, h4, h5, h6, p"):
            try:
                tag_name = element.root.tag
                if tag_name.startswith("h"):
                    level = int(tag_name[1])
                else:
                    level = 0

                text = element.css("::text").get()
                if text:
                    text = text.strip()
                    content_parts.append(f"{'#' * level} {text}\n\n")

            except Exception as e:
                print(e)
                logger.error(f"{e} \n url: {response.url}, element: {element}")

        return "".join(content_parts)