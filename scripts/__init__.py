from app.repository.db import db

from .recrawl_js import get_urls_for_rescraping


def run_conversion():
    get_urls_for_rescraping(db)