import scrapy
from scrapy.crawler import CrawlerProcess

class PDFHtmlLinkSpider(scrapy.Spider):
    name = 'pdf_html_link_spider'
    allowed_domains = ['puc.paris']
    start_urls = ['https://puc.paris']
    collected_links = set()
    visited_links = set()

    def parse(self, response):
        for href in response.css('a::attr(href)').getall():
            url = response.urljoin(href)
            if not url.startswith("http"):
                continue
            if not any(domain in url for domain in self.allowed_domains):
                continue
            if url.endswith(".pdf") or "text/html" in response.headers.get('Content-Type', b'').decode('utf-8'):
                if url not in self.collected_links:
                    self.collected_links.add(url)
                    #print(f"Collected link: {url}")
            if not url.endswith(".pdf"):
                yield scrapy.Request(url, callback=self.parse, dont_filter=True)

    def closed(self, reason):
        """Callback function called when the spider is closed."""
        print(f"Total number of unique links collected: {len(self.collected_links)}")
        # Optionally, save the links to a file
        with open("collected_links.txt", "w") as f:
            for link in sorted(self.collected_links):
                f.write(f"{link}\n")
        print("Links have been saved to collected_links.txt")


# Start the crawling process
process = CrawlerProcess(settings={
    "LOG_LEVEL": "INFO",  # Reduce log output for easier viewing of results
})
process.crawl(PDFHtmlLinkSpider)
process.start()
