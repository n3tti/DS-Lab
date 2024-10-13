# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

import csv
import uuid
import json




class FilterURLPipeline():
    
    def __init__(self):
        self.allowed_content_type = {None, "text/html", "application/pdf", "image/png"}

    def process_item(self, item, spider):
        if item["status"] != 200:
            DropItem()
        if item["content_type"] not in self.allowed_content_type:
            DropItem()
        return item


class IDAssignmentPipeline:
    def __init__(self):
        self.seen_urls = {}

    def process_item(self, item, spider):
        if item["url"] not in self.seen_urls.keys():
            id = self.get_next_id()
            item["id"] = id
            self.seen_urls[item["url"]] = id
        else:
            item["id"] = self.seen_urls[item["url"]]

        for child_url in item["child_urls"].keys():
            if child_url not in self.seen_urls.keys():
                id = self.get_next_id()
                item["child_urls"][child_url] = id
                self.seen_urls[child_url] = id
            else:
                item["child_urls"][child_url] = self.seen_urls[child_url]
        return item
    
    def get_next_id(self):
        return str(uuid.uuid1())  

class ParentsPipeline:
    def __init__(self):
        self.parents = {}
    
    def open_spider(self, spider):
        self.file = open('parents.json', 'w')

    def close_spider(self, spider):
        for child_id, parents_set in self.parents.items():
            dic = {"id" : child_id, "parents" : list(parents_set)}
            line = json.dumps(dic) + "\n"
            self.file.write(line)
        self.file.close()

    def process_item(self, item, spider):
        for child_id in item["child_urls"].values():
            if child_id not in self.parents.keys():
                self.parents[child_id] = set(item["id"])
            else:
                self.parents[child_id].add(item["id"])      
        return item


class DuplicatesPipeline:
    def process_item(self, item, spider):
        ## TODO, maybe with the hash thing -> compare the hash of item["body"]
        # the problem here is to determine which one of the duplicates to keep (as both duplicates can have different id's)
        return item
    
class MetadataPipeline:

    def open_spider(self, spider):
        self.file = open('metadata.json', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        dic = {"id": item["id"], "depth" : item["depth"], "url" : item["url"], "type" : item["content_type"], "length" : item["content_length"], \
               "encoding" : item["content_encoding"], "last_modified" : item["last_modified"], "date" : item["date"]}
        line = json.dumps(dic) + "\n"
        self.file.write(line)
        return item
  
    
class DownloadContentPipeline:
    def process_item(self, item, spider):
        ## TODO depending on the content type (pdf, png, html...) put the "raw" content i.e item[body] in a special data folder
        # with e.g. name of the file = id and a folder for each content type. 
        return item



# ###-------------------------------------------------
# class CsvPipeline:
#     def __init__(self):
#         self.seen_urls = {}
#         self.parents_urls = {}

#     def process_item(self, item, spider):
#         parent_url = item.get('parent_url')
#         child_url = item.get('child_url')

#         if not child_url or not self.interesting_url(child_url):
#             return item
#         if not parent_url or not self.interesting_url(parent_url):
#             return item
        
#         child_id = None
#         if child_url not in self.seen_urls.keys():
#             child_id = self.get_next_id()
#             self.seen_urls[child_url] = child_id
#         else:
#             child_id = self.seen_urls[child_url]
        
#         parent_id = None
#         if parent_url not in self.seen_urls.keys():
#             parent_id = self.get_next_id()
#             self.seen_urls[parent_url] = parent_id
#         else:
#             parent_id = self.seen_urls[parent_url]

#         if child_id not in self.parents_urls.keys():
#             self.parents_urls[child_id] = set([parent_id])
#         else:
#             self.parents_urls[child_id].add(parent_id)

#         return item

#     def close_spider(self, spider):
#         self.file = open("urls.csv", "w", newline="", encoding="utf-8")
#         self.csv_writer = csv.writer(self.file)
#         self.csv_writer.writerow(["url_id", "url"])
#         for id in self.seen_urls.keys():
#             self.csv_writer.writerow([id, self.seen_urls[id]])
#         self.file.close()

#         self.file = open("parents.csv", "w", newline="", encoding="utf-8")
#         self.csv_writer = csv.writer(self.file)
#         self.csv_writer.writerow(["child","parents"])
#         for id in self.parents_urls.keys():
#             self.csv_writer.writerow([id, ','.join(self.parents_urls[id])])
#         self.file.close()

    
#     def interesting_url(self, url):
#         if url.startswith("mailto:") or url.endswith(".csv") or url.endswith(".jpg")\
#             or url.endswith(".png"):
#             return False
#         return True

#     def get_next_id(self):
#         return str(uuid.uuid1())  


