from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from crawler.items import PageItem
import pdb

class CrawlingSpider(CrawlSpider):
    name = "mycrawler"
    allowed_domains = ["admin.ch"]
    start_urls = ["https://www.admin.ch/"]


    rules = (
        Rule(LinkExtractor(allow=allowed_domains, deny=(
            r'\.docx$', r'\.xlsx$', r'\.pptx$', r'\.zip$', r'\.tar$', r'\.gz$', r'\.jpg$', 
            r'\.jpeg$', r'\.gif$', r'\.svg$', r'\.mp3$', r'\.mp4$', r'\.avi$', r'\.mov$', 
            r'\.wmv$', r'\.txt$', r'\.json$', r'\.csv$', r'\.xml$', r'^mailto:', r'\.js$', 
            r'\.css$', r'\.exe$', r'\.bin$'
        )), callback='parse_item', follow=True, process_request='add_parent_url'),
    )


    def parse_item(self, response, parent_url=[]):
        try:
            
            item = PageItem()
            item["id"] = None
            item["status"] = response.status
            item["depth"] = response.meta["depth"]
            item["url"] = response.url 
            item["parent_url"] = parent_url

            item["child_urls"] = {}
            item["cousin_urls"] = {}

            item["content_type"] = response.headers.get('Content-Type', b'').decode('utf-8') if response.headers.get('Content-Type') else None
            item["content_length"] = int(response.headers.get('Content-Length').decode('utf-8')) if response.headers.get('Content-Length') else None
            item["content_encoding"] = response.headers.get('Content-Encoding', b'').decode('utf-8') if response.headers.get('Content-Encoding') else None
            item["content_body"] = response.body
            item["last_modified"] = response.headers.get("Last-Modified").decode('utf-8') if response.headers.get('Last-Modified') else None
            item["date"] = response.headers.get('Date').decode('utf-8') if response.headers.get('Date') else None
            item["title"] = response.headers.get('Title').decode('utf-8') if response.headers.get('Title') else None

            item["content"] = ' '.join(response.css('p::text').getall())

            alternate_links = response.xpath('//link[@rel="alternate"]')
            languages_dict = {}
            for link in alternate_links:
                lang = link.xpath('@lang').get()
                href = link.xpath('@href').get()
                if lang and href:
                    languages_dict[lang] = response.urljoin(href)
            item['cousin_urls'] = languages_dict

            for link in response.css('a::attr(href)').getall():
                if link not in item["cousin_urls"].keys() and link != response.url:
                    child_url = response.urljoin(link)
                    item["child_urls"][child_url] = None
            pdb.set_trace()
            yield item

        except Exception as e:
            print(e)
            pdb.set_trace()
            yield None
            
            