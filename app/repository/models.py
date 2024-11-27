from datetime import datetime
from enum import Enum

from pydantic import field_validator  # , HttpUrl
from sqlalchemy import CHAR, Column, DateTime, LargeBinary
from sqlalchemy.sql import func
from sqlalchemy.types import JSON  # Correctly import JSON from sqlalchemy.types
from sqlmodel import Field, Relationship, SQLModel
from sqlmodel._compat import SQLModelConfig

from app.repository.utils import normalize_url


class BaseModel(SQLModel):
    class ConfigDict:
        from_attributes = True
        use_enum_values = True
        populate_by_name = False

    model_config = SQLModelConfig(from_attributes=True, validate_assignment=True)


class PageStatusEnum(str, Enum):
    DISCOVERED = "Discovered"
    PROCESSING = "Processing"
    COMPLETED = "Completed"  # completed crawling but not converted to Markdown
    FAILED = "Failed"
    REVISITED = "Revisited"
    # FINALIZED = "Finalized"  # goes after the status "Completed"


class LinkStatusEnum(str, Enum):
    DISCOVERED = "Discovered"
    PROCESSING = "Processing"
    FAILED = "Failed"
    DOWNLOADED = "Downloaded"
    PROCESSED = "Processed"

    # TEMPCOMPLETED = "TempCompleted"


class ScrapedPage(BaseModel, table=True):
    __tablename__ = "scraped_pages"

    id: int = Field(primary_key=True)

    url: str = Field(index=True, unique=True)
    status: PageStatusEnum = Field(default=PageStatusEnum.DISCOVERED)
    depth: int = Field()

    pdf_links: list["PDFLink"] = Relationship(back_populates="scraped_page")
    child_links: list["ChildParentLink"] = Relationship(back_populates="parent_link")
    image_links: list["ImageLink"] = Relationship(back_populates="scraped_page")

    cousin_urls_dict: dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON))

    response_status_code: int | None = Field(default=None, description="HTTP status code of the response")
    response_text: str | None = Field(default=None, description="Text portion of the HTTP response")
    response_body: bytes | None = Field(default=None, sa_type=LargeBinary(), description="Binary body of the HTTP response")

    # content_formatted_with_markdown: str | None = Field(default=None, description="Response text converted to Markdown.")

    response_content_type: str | None = Field(default=None, description="MIME type of the content")
    response_content_length: int | None = Field(default=None, description="Length of the response content in bytes")
    response_content_encoding: str | None = Field(default=None, description="Encoding of the response content")
    response_last_modified: str | None = Field(default=None, description="Last modified date of the response")
    response_date: str | None = Field(default=None, description="Date of the response")

    response_metadata_lang: str | None = Field(default=None, sa_column=CHAR(10), description="Language of the content derived from the HTML tag")
    response_metadata_title: str | None = Field(default=None, description="Title of the content")
    # response_metadata_content: str | None = Field(default=None, description="Actual content (body)")
    response_metadata_description: str | None = Field(default=None, description="Description of the content")
    response_metadata_keywords: str | None = Field(default=None, description="Keywords as String associated with the content")
    response_metadata_content_hash: str | None = Field(default=None, description="Hash of the response content")

    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now()))

    @field_validator("response_content_type", "response_content_encoding", "response_last_modified", "response_date", mode="before")
    @classmethod
    def decode_utf8(cls, v) -> str:
        if isinstance(v, bytes):
            result = v.decode("utf-8")
            return result
        return v

    @field_validator("response_content_length", mode="before")
    @classmethod
    def convert_length_to_int(cls, v) -> str:
        if isinstance(v, bytes):
            try:
                return int(v.decode("utf-8"))
            except ValueError:
                pass
        elif isinstance(v, int):
            return v
        return None

    # @property
    # def content_formatted_with_markdown(self):
    #     return self._content_formatted_with_markdown

    # @content_formatted_with_markdown.setter
    # def content_formatted_with_markdown(self, value: dict[str, str]):
    #     self._content_formatted_with_markdown = value

    def __str__(self):
        model_dict = self.model_dump(include={"id", "url", "status"})
        return f"{type(self).__name__}({model_dict})"


class PDFLink(BaseModel, table=True):
    __tablename__ = "pdf_links"

    id: int = Field(primary_key=True)

    scraped_page_id: int = Field(foreign_key="scraped_pages.id")
    url: str = Field(index=True, description="normalized url")
    lang: str | None = Field(sa_column=CHAR(10))
    status: LinkStatusEnum = Field(default=LinkStatusEnum.DISCOVERED)

    scraped_page: "ScrapedPage" = Relationship(back_populates="pdf_links")

    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now()))

    def __str__(self):
        model_dict = self.model_dump()
        return f"{type(self).__name__}({model_dict})"

    @field_validator("url", mode="before")
    @classmethod
    def _normalize_url(cls, v) -> str:
        return normalize_url(v)


class ChildParentLink(BaseModel, table=True):
    __tablename__ = "child_parent_links"

    id: int = Field(primary_key=True)

    parent_id: int = Field(foreign_key="scraped_pages.id", description="scraped_page.id")  # parent_id
    child_url: str = Field(index=True)

    parent_link: "ScrapedPage" = Relationship(back_populates="child_links")  # the scraped_page is a parent page

    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now()))

    def __str__(self):
        model_dict = self.model_dump()
        return f"{type(self).__name__}({model_dict})"

    @field_validator("child_url", mode="before")
    @classmethod
    def _normalize_url(cls, v) -> str:
        return normalize_url(v)


class ImageLink(BaseModel, table=True):
    __tablename__ = "image_links"

    id: int = Field(primary_key=True)
    url: str = Field(index=True)
    alt: str | None = Field(default=None)
    status: LinkStatusEnum = Field(default=LinkStatusEnum.DISCOVERED)

    scraped_page_id: int = Field(foreign_key="scraped_pages.id", description="Link to the parent page id")
    scraped_page: "ScrapedPage" = Relationship(back_populates="image_links")

    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now()))

    def __str__(self):
        model_dict = self.model_dump()
        return f"{type(self).__name__}({model_dict})"

    @field_validator("url", mode="before")
    @classmethod
    def _normalize_url(cls, v) -> str:
        return normalize_url(v)


# TODO: Review this
class MarkdownPage(BaseModel, table=True):
    __tablename__ = "md_pages"

    id: int = Field(primary_key=True)

    scraped_page_id: int = Field(foreign_key="scraped_pages.id")

    body_md: str = Field()
