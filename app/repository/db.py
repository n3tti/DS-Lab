from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.repository.models import User
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/example.db')

engine = create_engine(DATABASE_URL, echo=True, future=True)
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Session = scoped_session(session_factory)


class Database:
    def __init__(self, session):
        self.session = session

    def create_user(self, name, email):
        new_user = User(name=name, email=email)
        self.session.add(new_user)
        self.session.commit()
        return new_user

    def get_user(self, name):
        return self.session.query(User).filter(User.name == name).first()


    def create_item(self, description):
        new_item = Item(description=description)
        self.session.add(new_item)
        self.session.commit()
        return new_item

    def update_url(self, url_id, new_url):
        url = self.session.query(URL).filter(URL.id == url_id).first()
        if url:
            url.url = new_url
            self.session.commit()
            return url
        return None


db = Database(Session())