# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import logging

from scrapy import Spider
from scrapy.exceptions import DropItem
from simhash import Simhash

from app.repository.db import db
from app.repository.models import ScrapedPage, StatusEnum


class DiscoveredStoragePipeline:
    def process_item(self, scraped_page: ScrapedPage, spider: Spider) -> ScrapedPage:
        existing_page = db.get_scraped_page(url=scraped_page.url)

        if existing_page is None:
            created_page = db.create_scraped_page(scraped_page.model_dump())
            scraped_page.id = created_page.id  # set id to the scraped object
            return scraped_page

        elif existing_page.status == StatusEnum.COMPLETED:
            raise DropItem(f"url: '{scraped_page.url}' is already COMPLETED.")
        else:
            db.update_scraped_page_status(scraped_page_id=scraped_page.id, status=StatusEnum.REVISITED)

            scraped_page.id = existing_page.id  # set id to the scraped object
            return scraped_page


class FilterURLPipeline:
    def __init__(self):
        self.allowed_content_type = ["text/html"]

    def process_item(self, scraped_page: ScrapedPage, spider: Spider) -> ScrapedPage:

        logging.getLogger(spider.name).info(f"Processing url: {scraped_page}")

        if scraped_page.response_status_code != 200:
            db.update_scraped_page_status(scraped_page.id, StatusEnum.FAILED)
            raise DropItem(f"HTTP Status: {scraped_page.response_status_code}: {scraped_page}.")
        elif scraped_page.response_content_type is None:
            db.update_scraped_page_status(scraped_page.id, StatusEnum.FAILED)
            raise DropItem("Content_type is None.")
        elif not scraped_page.response_content_type.split(";")[0] in self.allowed_content_type:
            db.update_scraped_page_status(scraped_page.id, StatusEnum.FAILED)
            raise DropItem(f"Content type \"{scraped_page.response_content_type.split(';')[0]}\" is not allowed.")

        return scraped_page


class HashContentPipeline:
    def process_item(self, item, spider):
        if item["content"] is not None:
            item["hash"] = Simhash(item["content"]).value
        else:
            item["hash"] = None
            logging.getLogger(spider.name).error("No content for that page.")
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
#             else:
#                 os.makedirs(path)


class CompletedStoragePipeline:
    def process_item(self, scraped_page: ScrapedPage, spider: Spider) -> ScrapedPage:
        # SAVE EVERYTHING TO DB HERE POTENTIALLY?
        # For example PDFs is another table, BUT the ScrapedPage is successfully processed only when PDF are safely saved to DB. I.e. one of the mandatory conditions is to save PDFs.
        # PARENT-CHILDs table too? I think. They should be implemented with a CURSOR.

        # ###################################### PDFPipeline HERE
        # for url in scraped_page.pdf_links_dict.keys():

        # ###################################### ImagePipeline HERE
        # for img_url, img_id in scraped_page.embedded_images_dict.items():
        #     dic = {"id": img_id, "url": img_url, "alt": scraped_page.img_alt, "parent": scraped_page.id}

        # ###################################### ContentPipeline HERE -- ContentPipeline is used by HashPipeline!!!!
        # if scraped_page.content_formatted_with_markdown:
        #     scraped_page.content_formatted_with_markdown = "\n".join(line.strip() for line in scraped_page.content_formatted_with_markdown.split("\n") if line.strip())

        # ###################################### MetadataPipeline HERE
        # keys_to_save = [
        #     # "id",
        #     # "depth",
        #     # "url",
        #     "response_content_type",
        #     "response_content_length",
        #     "response_content_encoding",
        #     "response_last_modified",
        #     "response_date",
        #     # "cousin_urls",
        #     "response_metadata_lang",
        #     "response_metadata_title",
        #     "response_metadata_content",
        #     "response_metadata_description",
        #     "response_metadata_keywords",
        #     "response_metadata_content_hash",
        #     # "pdf_links",
        #     # "embedded_images",
        # ]
        # dic = {}
        # for key in keys_to_save:
        #     dic[key] = getattr(scraped_page, key)

        # for url in scraped_page.child_urls_dict:
        #     dic = {"child_id": "ID_12334", "parent": scraped_page.id, "url": url}

        # WRITE EVERYTHING HERE I THINK:
        db.create_pdf_and_child_parent_links_and_update_status(
            scraped_page_id=scraped_page.id, pdf_urls=scraped_page.pdf_urls, child_urls=scraped_page.child_urls
        )

        return scraped_page


class TEMPPipeline:  ## TEMP Final Pipeline
    def process_item(self, scraped_page: ScrapedPage, spider: Spider) -> ScrapedPage:
        db.update_scraped_page_status(scraped_page_id=scraped_page.id, status=StatusEnum.TEMPCOMPLETED)

        return scraped_page
