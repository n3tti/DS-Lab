# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import csv
import uuid


class CrawlerPipeline:
    def process_item(self, item, spider):
        return item

class CsvPipeline:
    def __init__(self):
        self.seen_urls = {}
        self.parents_urls = {}

    def process_item(self, item, spider):
        parent_url = item.get('parent_url')
        child_url = item.get('child_url')

        if not child_url or not self.interesting_url(child_url):
            return item
        if not parent_url or not self.interesting_url(parent_url):
            return item
        
        child_id = None
        if child_url not in self.seen_urls.keys():
            child_id = self.get_next_id()
            self.seen_urls[child_url] = child_id
        else:
            child_id = self.seen_urls[child_url]
        
        parent_id = None
        if parent_url not in self.seen_urls.keys():
            parent_id = self.get_next_id()
            self.seen_urls[parent_url] = parent_id
        else:
            parent_id = self.seen_urls[parent_url]

        if child_id not in self.parents_urls.keys():
            self.parents_urls[child_id] = set([parent_id])
        else:
            self.parents_urls[child_id].add(parent_id)

        return item

    def close_spider(self, spider):
        self.file = open("urls.csv", "w", newline="", encoding="utf-8")
        self.csv_writer = csv.writer(self.file)
        self.csv_writer.writerow(["url_id", "url"])
        for id in self.seen_urls.keys():
            self.csv_writer.writerow([id, self.seen_urls[id]])
        self.file.close()

        self.file = open("parents.csv", "w", newline="", encoding="utf-8")
        self.csv_writer = csv.writer(self.file)
        self.csv_writer.writerow(["child","parents"])
        for id in self.parents_urls.keys():
            self.csv_writer.writerow([id, ','.join(self.parents_urls[id])])
        self.file.close()

    
    def interesting_url(self, url):
        if url.startswith("mailto:") or url.endswith(".csv") or url.endswith(".jpg")\
            or url.endswith(".png"):
            return False
        return True

    def get_next_id(self):
        return str(uuid.uuid1())  
