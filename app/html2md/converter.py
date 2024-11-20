import os
from markdownify import markdownify as md
from app.repository.db import session_scope, Database
from app.repository.models import PageStatusEnum, ScrapedPage, MarkdownPage
from app.config import DATA_DIR
from sqlalchemy.sql import text

class HTMLToMarkdownConverter:
    def __init__(self, db: Database):
        self.db = db
        
    def convert_html_to_markdown(self, html_content: str, page_id: int, session) -> str:
        """Convert HTML content to Markdown and save to database"""
        markdown_content = md(html_content)
        
        markdown_page = session.query(MarkdownPage).filter(
            MarkdownPage.scraped_page_id == page_id
        ).first()
        
        if markdown_page:
            markdown_page.body_md = markdown_content
        else:
            markdown_page = MarkdownPage(
                scraped_page_id=page_id,
                body_md=markdown_content
            )
            session.add(markdown_page)

        print(f"converting page {page_id}")
        
        return markdown_page
        
  
        



    def process_all_pages(self):
        """Process all HTML pages from database"""
        with session_scope() as session:
            # Query ScrapedPage records with HTML content
            pages = session.query(ScrapedPage).all()
                
            for page in pages:
               
                try:
                    html_content = page.response_body.decode('utf-8')
    
                    self.convert_html_to_markdown(
                        html_content,
                        page.id,
                        session
                    )
                except Exception as e:
                    print(f'Error converting page {page.id}: {str(e)}')