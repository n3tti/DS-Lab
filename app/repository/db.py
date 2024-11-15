from contextlib import contextmanager
from typing import Any

from pydantic import HttpUrl
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.config import DATABASE_URL
from app.repository.models import ChildParentLink, PageStatusEnum, PDFLink, ScrapedPage
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


class DatabaseException(Exception): ...


class Database:
    def create_scraped_page(self, scraped_page: ScrapedPage) -> ScrapedPage:
        with session_scope() as session:
            session.add(scraped_page)
            session.flush()
            return scraped_page.model_copy(deep=True)

    def update_scraped_page_status(self, scraped_page_id: int, status: PageStatusEnum):
        with session_scope() as session:
            scraped_page_obj = session.query(ScrapedPage).filter(ScrapedPage.id == scraped_page_id).first()
            if scraped_page_obj is None:
                return None
            scraped_page_obj.status = status

    def get_scraped_page(self, url) -> ScrapedPage | None:
        with session_scope() as session:
            scraped_page_obj = session.query(ScrapedPage).filter(ScrapedPage.url == url).first()
            if scraped_page_obj is None:
                return None

            return scraped_page_obj.model_copy(deep=True)


db = Database()
