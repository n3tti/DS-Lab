import logging, pdb
from urllib.parse import urljoin

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_playwright.page import PageMethod
from scrapy.http import Request

from app.repository.models import ScrapedPage

logger = logging.getLogger(__name__.split(".")[-1])


class CrawlingSpider(CrawlSpider):

    name = "fedlex_crawler"
    allowed_domains = ["fedlex.admin.ch"]
    start_urls = ["https://www.fedlex.admin.ch/de/faq/cc/pdf-documents", #"https://www.ch.ch/de/steuern-und-finanzen/steuerarten/mehrwertsteuer/#", "https://www.admin.ch/"
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                url,
                meta=dict(
                    playwright=True,
                    playwright_include_page=True,
                    playwright_page_methods=[
                        # Wait for initial load
                        PageMethod("wait_for_selector", "body"),
                        # Wait for JavaScript to initialize
                        PageMethod("wait_for_timeout", 5000),
                        # Accept any cookies/terms if needed
                        # PageMethod("click", ".accept-button"),  # Adjust if needed
                        # Wait for content to be available
                        PageMethod("wait_for_load_state", "networkidle"),
                        PageMethod("wait_for_timeout", 2000),
                    ],
                    errback=self.errback,
                ),
            )

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
        logger.error(f"Request failed: {failure.value}")

    def parse_start_url(self, response):
        return self.parse_item(response)

    rules = (
        Rule(
            LinkExtractor(
                allow_domains=allowed_domains,
                allow=r".*\.html?$|.*/$|.*(?<!\.)\w+$",
            ),
            callback="parse_item",
            follow=True,
            process_request="process_request",
        ),
    )

    def process_request(self, request, spider):
        request.meta.update(
            playwright=True,
            playwright_include_page=True,
            playwright_page_methods=[
                PageMethod("wait_for_selector", "body"),
                PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                PageMethod("wait_for_timeout", 2000),
            ],
            errback=self.errback,
        )
        return request

    def parse_item(self, response):

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

            # get pdf links of this page
            if full_url.lower().endswith(".pdf"):
                pdf_urls.append(full_url)

        #####################################################
        child_urls = []
        for link in response.css("a::attr(href)").getall():
            full_url = urljoin(response.url, link)

            # get child and cousin urls
            # TBD: can't it be just `full_url.lower().endswith(".pdf")` <-> `link not in pdf_urls.keys()` ?
            if link not in cousin_urls_dict.keys() and link not in pdf_urls and link != response.url:
                child_urls.append(full_url)

        #####################################################
        embedded_images, img_alt_dict = self.extract_images(response)

        #####################################################
        content_formatted_with_markdown = self.format_content_with_markdown(response)

        #####################################################
        lang = response.xpath("//html/@lang").get()
        if not lang:
            # Try meta tag if html lang is not found
            lang = response.xpath("//meta[@http-equiv='content-language']/@content | //meta[@property='og:locale']/@content").get()

        #####################################################
        # TODO: Change to hasattr
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
            response_text=response.text,
            # response_body=response.body,
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

    # handle embedded images
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

    # extract title from multiple sources
    def get_title(self, response):
        """Extract title from multiple possible sources"""
        title = response.headers.get("Title", b"").decode("utf-8") or response.css("title::text").get() or response.css("h1::text").get() or ""
        return title.strip()

    # format content with markdown
    def format_content_with_markdown(self, response):
        """Format content with markdown, preserving the original order of elements"""
        content_parts = []

        # Select all headers and paragraphs in order of appearance
        for element in response.css("h1, h2, h3, h4, h5, h6, p"):
            try:
                # Get the element name (h1, h2, p, etc.)
                tag_name = element.root.tag

                # Handle headers
                if tag_name.startswith("h"):
                    level = int(tag_name[1])  # get number from h1, h2, etc.
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
