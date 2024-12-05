from app.repository.db import db

from .converter import HTMLToMarkdownConverter


def run_conversion():
    converter = HTMLToMarkdownConverter()
    converter.process_all_pages()
