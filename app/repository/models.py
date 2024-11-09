from enum import Enum
from sqlmodel import SQLModel, Field, JSON, Relationship
from sqlalchemy import LargeBinary, Column, DateTime, CHAR
from sqlalchemy.sql import func
from typing import Optional
from datetime import datetime
from pydantic import PrivateAttr



class BaseModel(SQLModel):
    class Config:
        from_attributes = True
        use_enum_values = True
        populate_by_name = False


class StatusEnum(str, Enum):
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"
    DISCOVERED = "Discovered"
    REVISITED = "Revisited"

    TEMPCOMPLETED = "TempCompleted"


class ScrapedPage(SQLModel, table=True):
    __tablename__ = 'scraped_pages'

    id: int = Field(primary_key=True)
    url: str = Field(index=True, unique=True)
    status: StatusEnum = Field(default=StatusEnum.DISCOVERED)

    pdf_links: list["PDFLink"] = Relationship(back_populates="scraped_pages")

    # TODO: CHANGE TO SETS
    _cousin_urls_dict: dict[str, str]#PrivateAttr()#Field(default_factory=dict, repr=False)#{}#PrivateAttr()#default_factory=dict)
    _pdf_links_dict: dict[str, str]#PrivateAttr()#Field(default_factory=dict, repr=False)#{}#PrivateAttr()#default_factory=dict)
    _child_urls_dict: dict[str, str]#PrivateAttr()#Field(default_factory=dict, repr=False)#{}#PrivateAttr()#default_factory=dict)
    _embedded_images_dict: dict[str, str]

    _img_alt: str | None = None



    response_status_code: int | None = Field(default=None, description="HTTP status code of the response")

    # metadata
    response_content_type: str | None = Field(default=None, description="Content type of the HTTP response")



    response_text: str | None = Field(default=None, description="Text portion of the HTTP response")
    response_content_body: bytes | None = Field(default=None, sa_type=LargeBinary(), description="Binary body of the HTTP response")


    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now()))


    def __str__(self):
        model_dict = self.dict(include={"id", "url", "status"})
        return str(model_dict)

    @property
    def cousin_urls_dict(self):
        return self._cousin_urls_dict

    @cousin_urls_dict.setter
    def cousin_urls_dict(self, value: dict[str, str]):
        self._cousin_urls_dict = value

    @property
    def pdf_links_dict(self):
        return self._pdf_links_dict

    @pdf_links_dict.setter
    def pdf_links_dict(self, value: dict[str, str]):
        self._pdf_links_dict = value

    @property
    def child_urls_dict(self):
        return self._child_urls_dict

    @child_urls_dict.setter
    def child_urls_dict(self, value: dict[str, str]):
        self._child_urls_dict = value

    @property
    def embedded_images_dict(self):
        return self._embedded_images_dict

    @embedded_images_dict.setter
    def embedded_images_dict(self, value: dict[str, str]):
        self._embedded_images_dict = value

    @property
    def img_alt(self):
        return self._img_alt

    @img_alt.setter
    def img_alt(self, value: dict[str, str]):
        self._img_alt = value


    # class Config:
    #     populate_by_name = True



class PDFLink(SQLModel, table=True):
    __tablename__ = 'pdf_links'
    id: int = Field(primary_key=True)
    url: str = Field(index=True)
    lang: str = Field(sa_column=CHAR(2))

    scraped_page_id: int = Field(default=None, foreign_key="scraped_pages.id")
    scraped_pages: "ScrapedPage" = Relationship(back_populates="pdf_links")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def __str__(self):
        return f"PDFLink(id={self.id}, url={self.url}, lang={self.lang}, scraped_page_id={self.scraped_page_id})"
