from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.repository.models import ScrapedPage, StatusEnum
import os
from contextlib import contextmanager

from typing import Any

from app.config import DATABASE_URL


engine = create_engine(DATABASE_URL, echo=False, future=True)
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Session = scoped_session(session_factory)



@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

class DatabaseException(Exception):
    ...



class Database:
    def create_scraped_page(self, scraped_page_data: dict[str, Any]):
        with session_scope() as session:
            scraped_page = ScrapedPage(**scraped_page_data)
            session.add(scraped_page)
            session.commit()
            return scraped_page

    def update_scraped_page_status(self, url: str, status: StatusEnum):
        with session_scope() as session:
            scraped_page_obj = session.query(ScrapedPage).filter(ScrapedPage.url == url).first()
            if scraped_page_obj is None:
                return None

            scraped_page_obj.status = status
            session.commit()

    def get_scraped_page(self, url):
        with session_scope() as session:
            scraped_page_obj = session.query(ScrapedPage).filter(ScrapedPage.url == url).first()
            if scraped_page_obj is None:
                return None
            return ScrapedPage.parse_obj(scraped_page_obj)


db = Database()
