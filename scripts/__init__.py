from .getErrorUrls import GetErrorUrls
from app.repository.db import db
from .export_markdown import export_markdown_files
import process_html_to_markdown

def get_error_urls():
    get_error_urls = GetErrorUrls(db)
    get_error_urls.populate_non_standard_status_codes()

def export_markdown():
    export_markdown_files()

def process_html_to_md():
    process_html_to_markdown()