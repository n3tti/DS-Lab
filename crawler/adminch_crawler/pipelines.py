# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import csv
import json
import logging
import os
import uuid
from abc import ABC



from adminch_crawler.config import (
    APPLICATION_DIR,
    IMAGE_DIR,
    METADATA_DIR,
    PARENTS_DIR,
    TEXT_DIR,
    JOBDIR,
    SAVE_IDS_FILE,
    SAVE_LAST_ID_FILE,
    PDF_FILE
)

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import logformatter
from scrapy.exceptions import DropItem
from simhash import Simhash


class ResummablePipeline(ABC):
    def __init__(self):
        self.files = {}

    def is_resuming(self, spider):
        return spider.is_resumingaf()
    
    def open_file(self, file, append):
        if append:
            self.files[file] = open(file, "a")
        else:
            self.files[file] = open(file, "w")

    def load_data(self, file):
        return json.load(self.files[file])

    def save_data(self, file, data):
        self.files[file].write(data)
    
    def close_files(self):
        for file_name, file in self.files.items():
            file.close()

#-------------------------------------------------

class FilterURLPipeline():

    def __init__(self):
        self.allowed_content_type = ["text/html"]

    def process_item(self, item, spider):
        if item["status"] != 200 or item["content_type"] is None:
            raise DropItem()
        elif not item["content_type"].split(";")[0] in self.allowed_content_type:
            logging.getLogger(spider.name).error("Unallowed content type.")
            raise DropItem()
        else:
            return item


class IDAssignmentPipeline(ResummablePipeline):

    def __init__(self):
        super().__init__()
        self.seen_urls = {}
        self.url_dics = ["pdf_links", "child_urls"]
        self.current_id = 0
        
    def process_item(self, item, spider):
        if item["url"] is None:
            logging.getLogger(spider.name).error("None URL")
            raise DropItem()
        
        if item["url"] not in self.seen_urls.keys() :
            id = self.get_next_id()
            item["id"] = id
            self.seen_urls[item["url"]] = id
        else:
            item["id"] = self.seen_urls[item["url"]]

        for url_dic in self.url_dics:
            for url in item[url_dic].keys():
                if url not in self.seen_urls.keys():
                    id = self.get_next_id()
                    self.seen_urls[url] = id
                    item[url_dic][url] = id
                else :
                    item[url_dic][url] = self.seen_urls[url]
        
        for lang, url in item["cousin_urls"].items():
            if url not in self.seen_urls.keys():
                id = self.get_next_id()
                self.seen_urls[url] = id
                item["cousin_urls"][lang] = id
            else :
                item["cousin_urls"][lang] = self.seen_urls[url]
        
        return item
    
    def get_next_id(self):
        self.current_id += 1
        return self.current_id
    
    def open_spider(self, spider):
        if self.is_resuming(spider):
            logging.getLogger(spider.name).error("RESUMING")
            self.open_file(SAVE_IDS_FILE, False)
            self.open_file(SAVE_LAST_ID_FILE, False)
            self.seen_urls = self.load_data(SAVE_IDS_FILE)
            self.current_id = self.load_data(SAVE_LAST_ID_FILE)["last_id"]
        else:
            self.open_file(SAVE_IDS_FILE, False)
            self.open_file(SAVE_LAST_ID_FILE, False)

    def close_spider(self, spider):
        self.save_data(SAVE_IDS_FILE, json.dumps(self.seen_urls))
        self.save_data(SAVE_LAST_ID_FILE, json.dumps({"last_id" : self.current_id}))
        self.close_files()
        

  
    # def process_item(self, item, spider):
    #     if item["url"] not in self.seen_urls.keys():
    #         id = self.get_next_id()
    #         item["id"] = id
    #         self.seen_urls[item["url"]] = id
    #     else:
    #         item["id"] = self.seen_urls[item["url"]]

    #     for child_url in item["child_urls"].keys():
    #         if child_url not in self.seen_urls.keys():
    #             id = self.get_next_id()
    #             item["child_urls"][child_url] = id
    #             self.seen_urls[child_url] = id
    #         else:
    #             item["child_urls"][child_url] = self.seen_urls[child_url]

    #     for lang, cousin_url in item["cousin_urls"].items():
    #         if cousin_url not in self.seen_urls.keys():
    #             id = self.get_next_id()
    #             item["cousin_urls"][lang] = id
    #             self.seen_urls[cousin_url] = id
    #         else:
    #             item["cousin_urls"][lang] = self.seen_urls[cousin_url]

    #     return item



class PDFPipeline(ResummablePipeline):
    def __init__(self):
        super().__init__()
        
    def open_spider(self, spider):
        if self.is_resuming(spider):
            self.open_file(PDF_FILE, True)
        else:
            self.open_file(PDF_FILE, False)

    def close_spider(self, spider):
        self.close_files()

    def process_item(self, item, spider):
        for pdf_url, id in item["pdf_links"].items():
            dic = {"id" : id, "url" : pdf_url, "lang" : item["lang"], "parent" : item["id"]}
            line = json.dumps(dic)
            self.save_data(PDF_FILE, line + "\n")
        return item



class HashContentPipeline:
    def process_item(self, item, spider):
        if item["content"] is not None:
            item["hash"] = Simhash(item["content"]).value
        else:
            item["hash"] = None
            logging.getLogger(spider.name).error("No content for that page.")
        return item



class ParentsPipeline(ResummablePipeline):
    def __init__(self):
        super().__init__()

    def open_spider(self, spider):
        if self.is_resuming(spider):
            self.open_file(PARENTS_DIR, True)
        else:
            self.open_file(PARENTS_DIR, False)

    def close_spider(self, spider):
        self.close_files()

    def process_item(self, item, spider):
        for child_id in item["child_urls"].values():
            dic = {"id": child_id, "parent": item["id"]}
            line = json.dumps(dic)
            self.save_data(PARENTS_DIR, line + '\n')
        return item


class MetadataPipeline(ResummablePipeline):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def open_spider(self, spider):
        if self.is_resuming(spider):
            self.open_file(METADATA_DIR, True)
        else:
            self.open_file(METADATA_DIR, False)

    def close_spider(self, spider):
        self.close_files()

    def process_item(self, item, spider):
        keys_to_save = [
            "id",
            "depth",
            "url",
            "lang",
            "content_type",
            "content_length",
            "content_encoding",
            "last_modified",
            "date",
            "hash",
            "cousin_urls",
            "title",
            "content",
            "description",
            "keywords",
            "pdf_links",
        ]
        dic = {}
        for key in keys_to_save:
            if key in item:
                dic[key] = item[key]
            else:
                self.logger.warning(f"Key '{key}' not found in item.")
                dic[key] = None

        line = json.dumps(dic)
        self.save_data( METADATA_DIR, line + '\n')
        return item


# class DownloadContentPipeline:
#     def __init__(self):
#         self.folders = [TEXT_DIR, IMAGE_DIR, APPLICATION_DIR]
#         self.content_types = ["text/html", "application/pdf", "image/png"]

#     def process_item(self, item, spider):
#         content_type = item["content_type"].split(";")[0]

#         if content_type == "text/html":
#             with open(TEXT_DIR + f"{item['id']}.bin", "wb") as file:
#                 file.write(item["content_body"])

#         return item

#     def open_spider(self, spider):
#         self.clean_folders()

#     def clean_folders(self):
#         for path in self.folders:
#             if os.path.exists(path):
#                 for filename in os.listdir(path):
#                     file_path = os.path.join(path, filename)
#                     try:
#                         if os.path.isfile(file_path) or os.path.islink(file_path):
#                             os.unlink(file_path)
#                     except Exception as e:
#                         print(f"Failed to delete {file_path}. Reason: {e}")
#             else:
#                 os.makedirs(path)
