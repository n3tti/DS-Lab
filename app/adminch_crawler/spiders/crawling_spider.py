from urllib.parse import urljoin

from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_playwright.page import PageMethod

import html2text

from app.logs import logger
from app.repository.models import ChildParentLink, ImageLink, PDFLink, ScrapedPage


class CrawlingSpider(CrawlSpider):

    name = "my2crawler"
    allowed_domains = ["admin.ch"]
    start_urls = ["https://www.admin.ch/"]

    ############################### Code for Playwright ##############################
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
    ############################### End of code for Playwright" ##############################

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
        image_links = []
        for img in response.css("img"):
            src = img.attrib.get("src")
            if src:
                full_url = urljoin(response.url, src)
                alt = img.attrib.get("alt", "")
                image_links.append(ImageLink(url=full_url, alt=alt))

        #####################################################
        converter = html2text.HTML2Text()
        converter.ignore_links = True    # Include links in the output
        converter.ignore_images = True   # Include image placeholders
        converter.ignore_tables = False   # Include tablese
        converter.protect_links = True    # Prevent splitting of links
        content_formatted_with_markdown = converter.handle(response.text)

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
            pdf_links=[PDFLink(url=x, lang=lang) for x in pdf_urls],
            child_links=[ChildParentLink(child_url=x) for x in child_urls],
            image_links=image_links,
            cousin_urls_dict=cousin_urls_dict,
            depth=response.meta["depth"],
            response_status_code=response.status,
            response_text=response.text,
            response_body=response.body,
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

            content_formatted_with_markdown=content_formatted_with_markdown,
        )

        # TODO: discuss if we need this, later make a migration if needed
        # scraped_page.content_formatted_with_markdown = content_formatted_with_markdown

        yield scraped_page

    # extract title from multiple sources
    def get_title(self, response):
        """Extract title from multiple possible sources"""
        title = response.headers.get("Title", b"").decode("utf-8") or response.css("title::text").get() or response.css("h1::text").get() or ""
        return title.strip()
