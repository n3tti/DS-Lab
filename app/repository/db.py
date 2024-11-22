from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.config import DATABASE_URL
from app.repository.models import PageStatusEnum, ScrapedPage

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

    def update_scraped_page_status(self, scraped_page_id: int, status: PageStatusEnum) -> None:
        with session_scope() as session:
            scraped_page_obj = session.query(ScrapedPage).filter(ScrapedPage.id == scraped_page_id).first()
            if scraped_page_obj is None:
                return None
            scraped_page_obj.status = status

    def get_scraped_page(self, url: str) -> ScrapedPage | None:
        with session_scope() as session:
            scraped_page_obj = session.query(ScrapedPage).filter(ScrapedPage.url == url).first()
            if scraped_page_obj is None:
                return None

            return scraped_page_obj.model_copy(deep=True)

    def get_scraped_page_by_id(self, scraped_page_id: int) -> ScrapedPage | None:
        with session_scope() as session:
            scraped_page_obj = session.query(ScrapedPage).filter(ScrapedPage.id == scraped_page_id).first()
            if scraped_page_obj is None:
                return None

            return scraped_page_obj.model_copy(deep=True)

    def get_scraped_page_unconverted_ids(self):
        with session_scope() as session:
            query = session.query(ScrapedPage.id).filter(ScrapedPage.status != PageStatusEnum.FINALIZED).order_by(ScrapedPage.id).yield_per(1000)
            for (page_id,) in query:
                yield page_id

    def update_scraped_page_with_markdown_content(self, scraped_page_id: int, markdown_content: str) -> None:
        with session_scope() as session:
            scraped_page_obj = session.query(ScrapedPage).filter(ScrapedPage.id == scraped_page_id).first()
            if scraped_page_obj is None:
                return None
            scraped_page_obj.content_formatted_with_markdown = markdown_content
            scraped_page_obj.status = PageStatusEnum.FINALIZED


db = Database()
