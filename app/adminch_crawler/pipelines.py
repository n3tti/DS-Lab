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



from app.config import (
    APPLICATION_DIR,
    IMAGE_DIR,
    IMAGE_FILE,
    # JOBDIR,
    METADATA_DIR,
    PARENTS_DIR,
    PDF_FILE,
    SAVE_IDS_FILE,
    SAVE_LAST_ID_FILE,
    TEXT_DIR,
)

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import logformatter
from scrapy.exceptions import DropItem
from simhash import Simhash

from app.repository.models import ScrapedPage, StatusEnum
from app.repository.db import db

from scrapy import Spider


# class ResummablePipeline(ABC):
#     def __init__(self):
#         self.files = {}

#     def is_resuming(self, spider):
#         return spider.is_resuming()

#     def open_file(self, file, append):
#         if append:
#             self.files[file] = open(file, "a")
#         else:
#             self.files[file] = open(file, "w")

#     def load_data(self, file):
#         f = open(file, "r")
#         data = json.load(f)
#         f.close()
#         return data

#     def save_data(self, file, data):
#         self.files[file].write(data)

#     def close_files(self):
#         for file_name, file in self.files.items():
#             file.close()


# -------------------------------------------------


class DiscoveredStoragePipeline:
    def process_item(self, scraped_page: ScrapedPage, spider: Spider) -> ScrapedPage:
        existing_page = db.get_scraped_page(url=scraped_page.url)

        if existing_page is None:
            created_page = db.create_scraped_page(scraped_page.dict())
            scraped_page.id = created_page.id  # set id to the scraped object
            return scraped_page

        elif existing_page.status == StatusEnum.COMPLETED:
            raise DropItem(f"url: '{scraped_page.url}' is already COMPLETED.")
        else:
            db.update_scraped_page_status(url=scraped_page.url, status=StatusEnum.REVISITED)

            scraped_page.id = existing_page.id  # set id to the scraped object
            return scraped_page


class FilterURLPipeline:
    def __init__(self):
        self.allowed_content_type = ["text/html"]

    def process_item(self, scraped_page: ScrapedPage, spider: Spider) -> ScrapedPage:

        logging.getLogger(spider.name).info(f"Processing url: {scraped_page}")

        if scraped_page.response_status_code != 200:
            raise DropItem(f"HTTP Status: {scraped_page.response_status_code}: {scraped_page}.")
        elif scraped_page.response_content_type is None:
            raise DropItem(f"Content_type is None.")
        elif not scraped_page.response_content_type.split(";")[0] in self.allowed_content_type:
            raise DropItem(f"Content type \"{scraped_page.response_content_type.split(';')[0]}\" is not allowed.")

        return scraped_page


class IDAssignmentPipeline:

    def __init__(self):
        super().__init__()
        # self.seen_urls = {}
        # self.url_dics = ["pdf_links", "child_urls"]
        self.url_dics = ["embedded_images", "pdf_links", "child_urls"]
        self.current_id = 0

    def process_item(self, scraped_page: ScrapedPage, spider: Spider) -> ScrapedPage:
        # if scraped_page.url is None:
        #     logging.getLogger(spider.name).error("None URL")
        #     raise DropItem()

        # if scraped_page.url not in self.seen_urls.keys():
            # id = self.get_next_id()
            # scraped_page.id = id
            # self.seen_urls[scraped_page.url] = id
        # else:
            # scraped_page.id = self.seen_urls[scraped_page.url]

        for url_dic in self.url_dics:
            for url in getattr(scraped_page, url_dic, {}).keys():
                existing_page = db.get_scraped_page(url=url)

                if existing_page is None:
                    new_page = db.create_scraped_page({"url": url})
                    getattr(scraped_page, url_dic)[url] = new_page.id
                else:
                    getattr(scraped_page, url_dic)[url] = existing_page.url

        for lang, url in scraped_page.cousin_urls.items():
            existing_page = db.get_scraped_page(url=url)

            if existing_page is None:
                new_page = db.create_scraped_page({"url": url})
                scraped_page.cousin_urls[lang] = new_page.id
            else:
                scraped_page.cousin_urls[lang] = existing_page.url

        return scraped_page

    # # def get_next_id(self):
    # #     self.current_id += 1
    # #     return self.current_id

    # # def open_spider(self, spider):
    # #     if self.is_resuming(spider):
    # #         self.seen_urls = self.load_data(SAVE_IDS_FILE)
    # #         self.current_id = self.load_data(SAVE_LAST_ID_FILE)["last_id"]

    # def close_spider(self, spider):
    #     # self.open_file(SAVE_IDS_FILE, False)
    #     # self.open_file(SAVE_LAST_ID_FILE, False)
    #     # self.save_data(SAVE_IDS_FILE, json.dumps(self.seen_urls))
    #     # self.save_data(SAVE_LAST_ID_FILE, json.dumps({"last_id": self.current_id}))
    #     self.close_files()

    # # def process_item(self, item, spider):
    # #     if item["url"] not in self.seen_urls.keys():
    # #         id = self.get_next_id()
    # #         item["id"] = id
    # #         self.seen_urls[item["url"]] = id
    # #     else:
    # #         item["id"] = self.seen_urls[item["url"]]

    # #     for child_url in item["child_urls"].keys():
    # #         if child_url not in self.seen_urls.keys():
    # #             id = self.get_next_id()
    # #             item["child_urls"][child_url] = id
    # #             self.seen_urls[child_url] = id
    # #         else:
    # #             item["child_urls"][child_url] = self.seen_urls[child_url]

    # #     for lang, cousin_url in item["cousin_urls"].items():
    # #         if cousin_url not in self.seen_urls.keys():
    # #             id = self.get_next_id()
    # #             item["cousin_urls"][lang] = id
    # #             self.seen_urls[cousin_url] = id
    # #         else:
    # #             item["cousin_urls"][lang] = self.seen_urls[cousin_url]

    # #     return item


# class PDFPipeline:

#     # def open_spider(self, spider):
#     #     if self.is_resuming(spider):
#     #         self.open_file(PDF_FILE, True)
#     #     else:
#             # self.open_file(PDF_FILE, False)

#     # def close_spider(self, spider):
#     #     self.close_files()

#     def process_item(self, scraped_page: ScrapedPage, spider: Spider) -> ScrapedPage:
#         for pdf_url in scraped_page.pdf_links_dict.keys():
#             print("pdf_url", pdf_url)
#         # for pdf_url, id in item["pdf_links"].items():
#             # CREATE A NEW OJBECT IN DB HERE
#             # new_pdf_link = db.create_pdf_link({
#             #     "url": pdf_url,
#             #     "lang": pdf_url["lang"],
#             #     "scraped_page_id": scraped_page.id,  # assuming the scraped page with ID 1 already exists in your database
#             # })
#             # print(new_pdf_link)
#             # dic = {"id": id, "url": pdf_url, "lang": item["lang"], "parent": item["id"]}
#             # line = json.dumps(dic)
#             # self.save_data(PDF_FILE, line + "\n")
#         return scraped_page



# class ImagePipeline:
#     def __init__(self):
#         super().__init__()

#     # def open_spider(self, spider):
#     #     if self.is_resuming(spider):
#     #         self.open_file(IMAGE_FILE, True)
#     #     else:
#     #         self.open_file(IMAGE_FILE, False)

#     # def close_spider(self, spider):
#     #     self.close_files()

#     def process_item(self, scraped_page: ScrapedPage, spider: Spider) -> ScrapedPage:
#         # for img_url, id in item["embedded_images"].items():
#         for img_url, img_id in scraped_page.embedded_images_dict.items():
#             dic = {"id": img_id, "url": img_url, "alt": scraped_page.img_alt, "parent": scraped_page.id}
#             print("my DIC", dic)
#             # line = json.dumps(dic)
#             # self.save_data(IMAGE_FILE, line + "\n")
#         return scraped_page


# class ContentPipeline:
#     def process_item(self, scraped_page: ScrapedPage, spider: Spider) -> ScrapedPage:
#         # Clean and validate content
#         if scraped_page.content_formatted_with_markdown:
#             scraped_page.content_formatted_with_markdown = "\n".join(line.strip() for line in scraped_page.content_formatted_with_markdown.split("\n") if line.strip())
#             print("content_formatted_with_markdown", scraped_page.content_formatted_with_markdown)
#         return scraped_page


class HashContentPipeline:
    def process_item(self, item, spider):
        if item["content"] is not None:
            item["hash"] = Simhash(item["content"]).value
        else:
            item["hash"] = None
            logging.getLogger(spider.name).error("No content for that page.")
        return item


class ParentsPipeline:
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
            self.save_data(PARENTS_DIR, line + "\n")
        return item


class MetadataPipeline:
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
            "embedded_images",
        ]
        dic = {}
        for key in keys_to_save:
            if key in item:
                dic[key] = item[key]
            else:
                self.logger.warning(f"Key '{key}' not found in item.")
                dic[key] = None

        line = json.dumps(dic)
        self.save_data(METADATA_DIR, line + "\n")
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


class CompletedStoragePipeline:
    def process_item(self, scraped_page: ScrapedPage, spider: Spider) -> ScrapedPage:
        # SAVE EVERYTHING TO DB HERE POTENTIALLY?

        # # PDFPipeline HERE
        # for url in scraped_page.pdf_links_dict.keys():
        #     print("pdf_url", url)

        # # ImagePipeline HERE
        # for img_url, img_id in scraped_page.embedded_images_dict.items():
        #     dic = {"id": img_id, "url": img_url, "alt": scraped_page.img_alt, "parent": scraped_page.id}

        # ContentPipeline HERE
        if scraped_page.content_formatted_with_markdown:
            scraped_page.content_formatted_with_markdown = "\n".join(line.strip() for line in scraped_page.content_formatted_with_markdown.split("\n") if line.strip())
            print("content_formatted_with_markdown", scraped_page.content_formatted_with_markdown)

        return scraped_page


class TEMPPipeline: ## TEMP Final Pipeline
    def process_item(self, scraped_page: ScrapedPage, spider: Spider) -> ScrapedPage:
        db.update_scraped_page_status(url=scraped_page.url, status=StatusEnum.TEMPCOMPLETED)

        return scraped_page

