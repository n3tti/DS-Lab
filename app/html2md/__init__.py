from app.repository.db import db

from .converter import HTMLToMarkdownConverter

from .modular import ReadabilityInscriptis
from .trafilatura import Trafilatura

def run_conversion():
    converter = HTMLToMarkdownConverter(db)
    converter.process_all_pages()


