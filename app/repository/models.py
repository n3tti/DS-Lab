from enum import Enum
from sqlmodel import SQLModel, Field, JSON
from sqlalchemy import LargeBinary, Column, DateTime
from sqlalchemy.sql import func
from typing import Optional
from datetime import datetime


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
    __tablename__ = 'scraped_page'

    id: int = Field(primary_key=True)
    url: str = Field(index=True, unique=True)
    status: StatusEnum = Field(default=StatusEnum.DISCOVERED)  # Application-specific status

    cousin_urls: dict[str, str | None] = Field(default_factory=dict, sa_column=Column(JSON), description="Dictionary of cousin URLs")
    pdf_links: dict[str, str | None] = Field(default_factory=dict, sa_column=Column(JSON), description="Dictionary of PDF links")
    child_urls: dict[str, str | None] = Field(default_factory=dict, sa_column=Column(JSON), description="Dictionary of child URLs")



    response_status_code: int | None = Field(default=None, description="HTTP status code of the response")

    # metadata
    response_content_type: str | None = Field(default=None, description="Content type of the HTTP response")



    response_text: str | None = Field(default=None, description="Text portion of the HTTP response")
    response_body: bytes | None = Field(default=None, sa_type=LargeBinary(), description="Binary body of the HTTP response")


    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now()))


    def __str__(self):
        model_dict = self.dict(include={"id", "url", "status"})
        return str(model_dict)
