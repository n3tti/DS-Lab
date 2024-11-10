from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.repository.models import ScrapedPage, StatusEnum, PDFLink, ChildParentLink
import os
from contextlib import contextmanager

from typing import Any
from pydantic import HttpUrl

from app.config import DATABASE_URL
from app.repository.utils import normalize_url


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
    def create_scraped_page(self, scraped_page_data: dict[str, Any]) -> ScrapedPage:
        with session_scope() as session:
            new_scraped_page = ScrapedPage(**scraped_page_data)
            session.add(new_scraped_page)
            session.flush()

            obj_id = new_scraped_page.id
            scraped_page_data['id'] = obj_id
            return ScrapedPage(**scraped_page_data)

    def update_scraped_page_status(self, scraped_page_id: int, status: StatusEnum):
        with session_scope() as session:
            scraped_page_obj = session.query(ScrapedPage).filter(ScrapedPage.id == scraped_page_id).first()
            if scraped_page_obj is None:
                return None
            scraped_page_obj.status = status

    def get_scraped_page(self, url):
        with session_scope() as session:
            scraped_page_obj = session.query(ScrapedPage).filter(ScrapedPage.url == url).first()
            if scraped_page_obj is None:
                return None

            return ScrapedPage.parse_obj(scraped_page_obj)

    def create_pdf_and_child_parent_links_and_update_status(self, scraped_page_id: int, pdf_urls: list[HttpUrl], child_urls: list[HttpUrl]):
        pdf_urls = [normalize_url(url) for url in pdf_urls]
        child_urls = [normalize_url(url) for url in child_urls]

        with session_scope() as session:
            scraped_page = session.query(ScrapedPage).filter(ScrapedPage.id == scraped_page_id).first()

            # if not session.contains(scraped_page):
            #     scraped_page = session.merge(scraped_page)

            for url in pdf_urls:
                pdf_link = PDFLink(url=url, lang=scraped_page.response_metadata_lang, scraped_page=scraped_page)
                session.add(pdf_link)

            for url in child_urls:
                child_link = ChildParentLink(child_url=url, parent_link=scraped_page)
                session.add(child_link)

            scraped_page.status = StatusEnum.COMPLETED


db = Database()
