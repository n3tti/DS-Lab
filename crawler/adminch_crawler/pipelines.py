# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import csv
import json
import logging
import os
import uuid
import pdb
import hashlib

from adminch_crawler.config import (
    APPLICATION_DIR,
    IMAGE_DIR,
    METADATA_DIR,
    PARENTS_DIR,
    TEXT_DIR,
)

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import logformatter
from scrapy.exceptions import DropItem
from simhash import Simhash


class FilterURLPipeline:

    def __init__(self):
        self.allowed_content_type = ["text/html"]

    def process_item(self, item, spider):
        if item["status"] != 200 or item["content_type"] is None:
            raise DropItem()
        elif not item["content_type"].split(";")[0] in self.allowed_content_type:
            logging.getLogger(spider.name).error(f"Unallowed content type. \n ContentType: {item['content_type']} \n url: {item['url']}")
            raise DropItem()
        else:
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

        for lang, cousin_url in item["cousin_urls"].items():
            if cousin_url not in self.seen_urls.keys():
                id = self.get_next_id()
                item["cousin_urls"][lang] = id
                self.seen_urls[cousin_url] = id
            else:
                item["cousin_urls"][lang] = self.seen_urls[cousin_url]

        return item

    def get_next_id(self):
        return str(uuid.uuid1())


class ParentsPipeline:
    def __init__(self):
        self.parents = {}

    def open_spider(self, spider):
        self.file = open(PARENTS_DIR, "w")

    def close_spider(self, spider):
        self.file.write("[\n")
        first = True
        for child_id, parents_set in self.parents.items():
            dic = {"id": child_id, "parents": list(parents_set)}
            line = json.dumps(dic)
            if first:
                first = False
            else:
                line = ",\n" + line
            self.file.write(line)
        self.file.write("\n]")
        self.file.close()

    def process_item(self, item, spider):
        for child_id in item["child_urls"].values():
            if child_id not in self.parents.keys():
                self.parents[child_id] = set()
                self.parents[child_id].add(item["id"])
            else:
                self.parents[child_id].add(item["id"])
        return item


class HashContentPipeline:

    def hash_text(self, text):
        # Create a SHA-256 hash of the input text
        return hashlib.sha256(text.encode()).hexdigest()

    def process_item(self, item, spider):
        try:
            if item["content"] is not None:
                item["hash"] = self.hash_text(item["content"])
            else:
                item["hash"] = None
                logging.getLogger(spider.name).error(f"No content for that page.\n Url: {item['url']}")
        except Exception as e:
            print(e)
            pdb.set_trace()
        return item


class DuplicatesPipeline:
    def process_item(self, item, spider):
        ## TODO, maybe with the hash thing -> compare the hash of item["body"]
        # the problem here is to determine which one of the duplicates to keep (as both duplicates can have different id's)
        return item


class MetadataPipeline:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def open_spider(self, spider):
        self.file = open(METADATA_DIR, "w")
        self.file.write("[\n")
        self.isFirst = True

    def close_spider(self, spider):
        self.file.write("\n]")
        self.file.close()

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
            "embedded_images"
        ]
        dic = {}
        for key in keys_to_save:
            if key in item:
                dic[key] = item[key]
            else:
                self.logger.warning(f"Key '{key}' not found in item.")
                dic[key] = None

        line = json.dumps(dic)
        if self.isFirst:
            self.isFirst = False
        else:
            line = ",\n" + line
        self.file.write(line)
        return item


class DownloadContentPipeline:
    def __init__(self):
        self.folders = [TEXT_DIR, IMAGE_DIR, APPLICATION_DIR]
        self.content_types = ["text/html", "application/pdf", "image/png"]

    def process_item(self, item, spider):
        content_type = item["content_type"].split(";")[0]

        if content_type == "text/html":
            with open(TEXT_DIR + f"{item['id']}.bin", "wb") as file:
                file.write(item["content_body"])

        return item

    def open_spider(self, spider):
        self.clean_folders()

    def clean_folders(self):
        for path in self.folders:
            if os.path.exists(path):
                for filename in os.listdir(path):
                    file_path = os.path.join(path, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        print(f"Failed to delete {file_path}. Reason: {e}")
            else:
                os.makedirs(path)

class ContentPipeline:
    def process_item(self, item, spider):
        # Clean and validate content
        if item.get('content'):
            # Remove excessive newlines and spaces
            item['content'] = '\n'.join(line.strip() for line in item['content'].split('\n') if line.strip())

        return item
