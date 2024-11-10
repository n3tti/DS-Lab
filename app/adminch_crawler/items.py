# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import PrivateAttr
from sqlalchemy import CHAR, Column, DateTime, LargeBinary
from sqlalchemy.sql import func
from sqlmodel import JSON, Field, Relationship, SQLModel

from app.repository.models import StatusEnum


class PageItem(SQLModel):
    id: int | None = None
    status: StatusEnum = StatusEnum.DISCOVERED
    depth: int
    # url: str

    response_status_code: int | None = None
    response_content_type: str | None = None
    response_content_length: int | None = None
    response_content_encoding: str | None = None
    response_last_modified: str | None = None
    response_date: str | None = None
    response_lang: str | None = None
    response_title: str | None = None

    cousin_urls_dict: dict[str, str | None] = {}
    pdf_links_dict: dict[str, str | None] = {}
    child_urls_dict: dict[str, str | None] = {}
    embedded_images_dict: dict[str, str | None] = {}

    response_content_body: bytes | None = None  # content_body = scrapy.Field()
    response_text: str | None = None  # content = scrapy.Field()

    content_hash: str | None = None  # hash = scrapy.Field()

    img_alt: str | None = None
    description: str | None = None
    keywords: list[str] | None = None

    def __str__(self):
        model_dict = self.dict(include={"id", "url", "status"})
        return str(model_dict)

    # def __repr__(self):
    #     return repr(
    #         {
    #             "id": self["id"],
    #             "status": self["status"],
    #             "depth": self["depth"],
    #             "url": self["url"],
    #             "content_type": self["content_type"],
    #         }
    #     )
