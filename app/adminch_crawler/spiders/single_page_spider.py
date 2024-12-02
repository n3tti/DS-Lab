import scrapy
from scrapy_playwright.page import PageMethod
from urllib.parse import urljoin
import json
from pathlib import Path
from datetime import datetime

# run with: scrapy crawl single_page_spider -a url=https://www.bit.admin.ch/en/sgc-en
class SinglePageSpider(scrapy.Spider):
    name = "single_page_spider"

    def __init__(self, url=None, output_dir="output", *args, **kwargs):
        super(SinglePageSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url]
        self.output_dir = output_dir

        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta=dict(
                    playwright=True,
                    playwright_include_page=True,
                    playwright_page_methods=[
                        PageMethod("wait_for_selector", "body"),
                        PageMethod("wait_for_load_state", "networkidle"),
                        PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                        PageMethod("wait_for_timeout", 2000),
                    ],
                ),
                callback=self.parse_page
            )

    async def parse_page(self, response):
        print("playwright is running")

        page = response.meta["playwright_page"]

        # Extract data similar to your existing spider
        title = response.css("title::text").get() or response.css("h1::text").get() or ""
        lang = response.xpath("//html/@lang").get() or response.xpath("//meta[@http-equiv='content-language']/@content").get()
        description = response.css('meta[name="description"]::attr(content)').get()
        keywords = response.css('meta[name="keywords"]::attr(content)').get()

        pdf_links = [urljoin(response.url, link) for link in response.css("a::attr(href)").getall() if link.lower().endswith(".pdf")]
        image_links = [{"url": urljoin(response.url, img.attrib.get("src")), "alt": img.attrib.get("alt", "")} for img in response.css("img")]
        child_links = [urljoin(response.url, link) for link in response.css("a::attr(href)").getall() if not link.lower().endswith(".pdf")]

        cousin_urls = {link.xpath("@lang").get(): response.urljoin(link.xpath("@href").get()) for link in response.xpath('//link[@rel="alternate"]')}

        content_formatted_with_markdown = self.format_content_with_markdown(response)

        result = {
            "url": response.url,
            "pdf_links": pdf_links,
            "image_links": image_links,
            "child_links": child_links,
            "cousin_urls_dict": cousin_urls,
            "metadata": {
                "lang": lang,
                "title": title.strip(),
                "description": description,
                "keywords": keywords,
            },
            "content_formatted_with_markdown": content_formatted_with_markdown
        }

        await page.close()

        # Generate filename based on timestamp and domain
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        domain = response.url.split("//")[-1].split("/")[0].replace(".", "_")
        filename = f"{self.output_dir}/{domain}_{timestamp}.json"

        # Save to JSON file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"Results saved to: {filename}")

    def format_content_with_markdown(self, response):
        content_parts = []
        for element in response.css("h1, h2, h3, h4, h5, h6, p"):
            tag_name = element.root.tag
            level = int(tag_name[1]) if tag_name.startswith("h") else 0
            text = element.css("::text").get()
            if text:
                content_parts.append(f"{'#' * level} {text.strip()}\n\n")
        return "".join(content_parts)