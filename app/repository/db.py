from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.repository.models import ScrapedPage, StatusEnum
import os
from contextlib import contextmanager

from typing import Any



DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/example.db')

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


    # def create_user(self, name, email):
    #     new_user = User(name=name, email=email)
    #     self.session.add(new_user)
    #     self.session.commit()
    #     return new_user

    # def get_user(self, name):
    #     return self.session.query(User).filter(User.name == name).first()


    # def create_item(self, description):
    #     new_item = Item(description=description)
    #     self.session.add(new_item)
    #     self.session.commit()
    #     return new_item

    # def update_url(self, url_id, new_url):
    #     url = self.session.query(URL).filter(URL.id == url_id).first()
    #     if url:
    #         url.url = new_url
    #         self.session.commit()
    #         return url
    #     return None


db = Database()