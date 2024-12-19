from contextlib import contextmanager

from sqlalchemy import create_engine, or_
from sqlalchemy.orm import scoped_session, sessionmaker

from app.config import DATABASE_URL
from app.repository.models import PageStatusEnum, ScrapedPage, PDFMetadata, LinkStatusEnum, PDFLink, FileStorage

engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args={'timeout':30})
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

    #---- Convert to MD ----
    def get_scraped_page_unconverted_to_md_ids(self):
        with session_scope() as session:
            query = session.query(ScrapedPage.id).filter(ScrapedPage.content_formatted_with_markdown.is_(None)).order_by(ScrapedPage.id).yield_per(1000)
            for (page_id,) in query:
                yield page_id

    def update_scraped_page_with_markdown_content(self, scraped_page_id: int, markdown_content: str) -> None:
        with session_scope() as session:
            scraped_page_obj = session.query(ScrapedPage).filter(ScrapedPage.id == scraped_page_id).first()
            if scraped_page_obj is None:
                return None
            scraped_page_obj.content_formatted_with_markdown = markdown_content
            # scraped_page_obj.status = PageStatusEnum.FINALIZED

    #---- PDF processing ----
    def update_pdf_status(self, pdf_id: int, status:LinkStatusEnum):
        with session_scope() as session:
            pdf_obj = session.query(PDFLink).filter(PDFLink.id == pdf_id).first()
            if pdf_obj is None:
                return None
            pdf_obj.status = status
    
    def add_processed_pdf(self, pdf_id : int, metadata: PDFMetadata, md, links, images, status : LinkStatusEnum):
        with session_scope() as session:
            pdf = session.query(PDFLink).filter(PDFLink.id == pdf_id).first()
            if pdf is None:
                return
            if status == LinkStatusEnum.FAILED or status == LinkStatusEnum.DOWNLOADED:
                pdf.status = status
            else:
                pdf.metadata_dict = metadata.dict()
                pdf.md_text = md
                pdf.referenced_links = links
                pdf.referenced_images = images
                pdf.status = LinkStatusEnum.PROCESSED
            session.flush()
                
    def get_unprocessed_pdf(self, row_per_read):
        with session_scope() as session:
            pdf_list = session.query(PDFLink).filter(PDFLink.status == LinkStatusEnum.DISCOVERED).limit(row_per_read).all()
            for pdf in pdf_list:
                pdf.status = LinkStatusEnum.PROCESSING
            if not pdf_list:
                return []
            session.flush()
            return [pdf.model_copy(deep=True) for pdf in pdf_list]
        
    def reset_processing(self):
        with session_scope() as session:
            pdf_list = session.query(PDFLink).filter(or_(PDFLink.status == LinkStatusEnum.PROCESSING, PDFLink.status == LinkStatusEnum.FAILED)).limit(500).all()
            if pdf_list is None or len(pdf_list) == 0:
                return False
            for pdf in pdf_list:
                pdf.status = LinkStatusEnum.DISCOVERED
            return True
    
    #---- File downloading ----
    def create_file_storage(self, file_storage: FileStorage) -> bool:
        with session_scope() as session:
            session.add(file_storage)
            session.flush()
            return True 

    #---- SIMHASH ----
    def reset_hash(self):
        with session_scope() as session:
            scraped_page_list = session.query(ScrapedPage).filter(ScrapedPage.response_metadata_content_hash == '0').limit(500).all()
            if scraped_page_list is None or len(scraped_page_list) == 0:
                return False
            for page in scraped_page_list:
                page.response_metadata_content_hash = None
            return True
    
    def get_none_hash(self, row_per_read):
        with session_scope() as session:
            scraped_page_list = session.query(ScrapedPage).filter(ScrapedPage.response_metadata_content_hash == None).limit(row_per_read).all()
            for page in scraped_page_list:
                page.response_metadata_content_hash = '0'
            if not scraped_page_list:
                return []
            session.flush()
            return [page.model_copy(deep=True) for page in scraped_page_list]
    
    def update_hash(self, id, hash):
        with session_scope() as session:
            page = session.query(ScrapedPage).filter(ScrapedPage.id == id).first()
            if page is None:
                return
            page.response_metadata_content_hash = hash
            session.flush()


db = Database()
