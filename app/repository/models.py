from enum import Enum
from sqlmodel import SQLModel, Field
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

    id: int = Field(default=None, primary_key=True)
    url: str = Field(index=True, unique=True)
    status: StatusEnum = Field(default=StatusEnum.DISCOVERED)  # Application-specific status

    response_status_code: Optional[int] = Field(default=None, description="HTTP status code of the response")

    # metadata
    response_content_type: Optional[str] = Field(default=None, description="Content type of the HTTP response")



    response_text: Optional[str] = Field(default=None, description="Text portion of the HTTP response")
    response_body: Optional[bytes] = Field(default=None, sa_type=LargeBinary(), description="Binary body of the HTTP response")


    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now()))


    def __str__(self):
        model_dict = self.dict(include={"id", "url", "status"})
        return str(model_dict)
