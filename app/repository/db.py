from contextlib import contextmanager
from typing import Any

from pydantic import HttpUrl
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.config import DATABASE_URL
from app.repository.models import ChildParentLink, PDFLink, ScrapedPage, PageStatusEnum, LinkStatusEnum, ImageLink, PDFMetadata
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
        
    def get_pdf_from_status(self, status_list) -> list[PDFLink]:
        with session_scope() as session:
            pdf_list = session.query(PDFLink).filter(PDFLink.status.in_(status_list)).all()
            if not pdf_list:
                return []
            return [pdf.model_copy(deep=True) for pdf in pdf_list]
        
    def update_pdf_status(self, pdf_id: int, status:LinkStatusEnum):
        with session_scope() as session:
            pdf_obj = session.query(PDFLink).filter(PDFLink.id == pdf_id).first()
            if pdf_obj is None:
                return None
            pdf_obj.status = status
    
    def add_pdf_md(self, pdf_id : int, metadata: PDFMetadata, md, links, images):
        with session_scope() as session:
            pdf = session.query(PDFLink).filter(PDFLink.id == pdf_id).first()
            if pdf is None:
                return
            pdf.metadata_dict = metadata
            pdf.md_text = md
            pdf.referenced_links = links
            pdf.referenced_images = images
            pdf.status = LinkStatusEnum.PROCESSED
               
    def add_image(self, img : ImageLink):
        with session_scope() as session:
            session.add(img)
            session.flush()
            return

        

db = Database()
