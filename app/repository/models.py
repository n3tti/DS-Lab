from enum import Enum
from sqlmodel import SQLModel, Field, JSON, Relationship
from sqlalchemy import LargeBinary, Column, DateTime, CHAR
from sqlalchemy.sql import func
from typing import Optional
from datetime import datetime
from pydantic import PrivateAttr, HttpUrl
from pydantic import field_validator, ValidationError
from sqlmodel._compat import SQLModelConfig



class BaseModel(SQLModel):
    class ConfigDict:
        from_attributes = True
        use_enum_values = True
        populate_by_name = False


class SQLModelValidation(BaseModel):
    """
    Helper class to allow for validation in SQLModel classes with table=True
    """
    model_config = SQLModelConfig(from_attributes=True, validate_assignment=True)


class StatusEnum(str, Enum):
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"
    DISCOVERED = "Discovered"
    REVISITED = "Revisited"

    TEMPCOMPLETED = "TempCompleted"





class ScrapedPage(SQLModelValidation, table=True):
    __tablename__ = 'scraped_pages'

    id: int = Field(primary_key=True)

    url: str = Field(index=True, unique=True)
    status: StatusEnum = Field(default=StatusEnum.DISCOVERED)
    depth: int = Field()

    pdf_link: list["PDFLink"] = Relationship(back_populates="scraped_page")
    child_link: list["ChildParentLink"] = Relationship(back_populates="parent_link")

    _cousin_urls_dict: dict[str, HttpUrl] = PrivateAttr(default_factory=dict)
    _pdf_urls: list[HttpUrl] = PrivateAttr(default_factory=list)
    _child_urls: list[HttpUrl] = PrivateAttr(default_factory=list)
    _embedded_images: list[HttpUrl] = PrivateAttr(default_factory=list)
    _img_alt_dict: dict[HttpUrl, str] = PrivateAttr(default_factory=dict)
    _content_formatted_with_markdown: str | None = PrivateAttr(default=None)

    response_status_code: int | None = Field(default=None, description="HTTP status code of the response")
    response_text: str | None = Field(default=None, description="Text portion of the HTTP response")
    response_body: bytes | None = Field(default=None, sa_type=LargeBinary(), description="Binary body of the HTTP response")

    response_content_type: str | None = Field(default=None, description="MIME type of the content")
    response_content_length: int | None = Field(default=None, description="Length of the response content in bytes")
    response_content_encoding: str | None = Field(default=None, description="Encoding of the response content")
    response_last_modified: str | None = Field(default=None, description="Last modified date of the response")
    response_date: str | None = Field(default=None, description="Date of the response")

    response_metadata_lang: str | None = Field(default=None, sa_column=CHAR(2), description="Language of the content derived from the HTML tag")
    response_metadata_title: str | None = Field(default=None, description="Title of the content")
    # response_metadata_content: str | None = Field(default=None, description="Actual content (body)")
    response_metadata_description: str | None = Field(default=None, description="Description of the content")
    response_metadata_keywords: list[str] = Field(default_factory=list, sa_column=Column(JSON), description="Keywords associated with the content")
    response_metadata_content_hash: str | None = Field(default=None, description="Hash of the response content")



    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now()))


    def __str__(self):
        model_dict = self.model_dump(include={"id", "url", "status"})
        return f"{type(self).__name__}({model_dict})"

    @classmethod
    @field_validator('response_content_type', 'response_content_encoding', 'response_last_modified', 'response_date', mode="before")
    def decode_utf8(cls, v) -> str:
        if isinstance(v, bytes):
            result = v.decode('utf-8')
            return result
        return v

    @field_validator('response_content_length', mode="before")
    @classmethod
    def convert_length_to_int(cls, v) -> str:
        if isinstance(v, bytes):
            try:
                return int(v.decode('utf-8'))
            except ValueError:
                pass
        elif isinstance(v, int):
            return v
        return None 

    # A lot of getters and setters below
    @property
    def cousin_urls_dict(self):
        return self._cousin_urls_dict

    @cousin_urls_dict.setter
    def cousin_urls_dict(self, value: dict[str, str]):
        self._cousin_urls_dict = value

    @property
    def pdf_urls(self):
        return self._pdf_urls

    @pdf_urls.setter
    def pdf_urls(self, value: dict[str, str]):
        self._pdf_urls = value

    @property
    def child_urls(self):
        return self._child_urls

    @child_urls.setter
    def child_urls(self, value: dict[str, str]):
        self._child_urls = value

    @property
    def embedded_images(self):
        return self._embedded_images

    @embedded_images.setter
    def embedded_images(self, value: dict[str, str]):
        self._embedded_images = value

    @property
    def img_alt_dict(self):
        return self._img_alt_dict_dict

    @img_alt_dict.setter
    def img_alt_dict(self, value: dict[str, str]):
        self._img_alt_dict = value

    @property
    def content_formatted_with_markdown(self):
        return self._content_formatted_with_markdown

    @content_formatted_with_markdown.setter
    def content_formatted_with_markdown(self, value: dict[str, str]):
        self._content_formatted_with_markdown = value



class PDFLink(SQLModelValidation, table=True):
    __tablename__ = 'pdf_links'

    id: int = Field(primary_key=True)

    url: str = Field(index=True)
    lang: str | None = Field(sa_column=CHAR(2))
    scraped_page_id: int = Field(default=None, foreign_key="scraped_pages.id")

    scraped_page: "ScrapedPage" = Relationship(back_populates="pdf_link")

    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now()))

    def __str__(self):
        model_dict = self.model_dump()
        return f"{type(self).__name__}({model_dict})"


class ChildParentLink(SQLModelValidation, table=True):
    __tablename__ = 'child_parent_links'

    id: int = Field(primary_key=True)

    parent_id: int = Field(default=None, foreign_key="scraped_pages.id", description="scraped_page.id")
    child_url: str = Field(index=True)

    parent_link: "ScrapedPage" = Relationship(back_populates="child_link")

    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now()))

    def __str__(self):
        model_dict = self.model_dump()
        return f"{type(self).__name__}({model_dict})"
