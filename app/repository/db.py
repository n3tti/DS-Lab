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
    def create_scraped_page(self, scraped_page_data: dict[str, Any]) -> ScrapedPage:
        with session_scope() as session:
            scraped_page = ScrapedPage(**scraped_page_data)
            obj_id = scraped_page.id

            session.add(scraped_page)
            session.commit()

            scraped_page_data['id'] = scraped_page.id
            return ScrapedPage(**scraped_page_data)

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

    def create_pdf_link(self, pdf_link_data: dict[str, Any]):
        """
        Creates a new PDFLink in the database.

        :param pdf_link_data: Dictionary containing the necessary data to create a PDFLink.
        :return: The created PDFLink object or None if the operation fails.
        """
        with session_scope() as session:
            # Create a new PDFLink object from the provided data
            pdf_link = PDFLink(**pdf_link_data)
            session.add(pdf_link)
            session.commit()

            return PDFLink.parse_obj(pdf_link)


db = Database()
