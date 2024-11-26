import os

from markdownify import markdownify as md
from sqlalchemy.sql import text

from bs4 import BeautifulSoup
import os
from pathlib import Path

from app.config import DATA_DIR
from app.repository.db import Database, session_scope
from app.repository.models import MarkdownPage, PageStatusEnum, ScrapedPage


class HTMLToMarkdownConverter:
    def __init__(self, db: Database):
        self.db = db

    def convert_html_to_markdown(self, html_content: str, page_id: int, session) -> str:
        """Convert HTML content to Markdown and save to database"""
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove unwanted elements - expanded list including breadcrumbs
        unwanted_elements = [
            # Navigation elements
            'header', 'nav', 'footer', 
            'breadcrumb', 'breadcrumbs',  # Common breadcrumb class names
            'nav[aria-label="breadcrumb"]',  # Bootstrap-style breadcrumbs
            'ol.breadcrumb',  # Another common breadcrumb pattern
            
            # UI/UX elements
            'menu', 'sidebar', 'aside',
            'social-share', 'service-navigation',
            'context-sidebar',
            
            # Technical elements
            'script', 'style', 'meta', 'link',
        ]
        
        # Remove elements by tag or class
        for element in soup.select(','.join(unwanted_elements)):
            element.decompose()
        
        # Additional cleanup for breadcrumbs that might use different patterns
        for element in soup.find_all(class_=lambda x: x and 
            ('bread' in x.lower() or 
             'navigation' in x.lower() or 
             'nav-' in x.lower())):
            element.decompose()
        
        # Get main content area
        main_content = soup.find(['main', 'article', 'div#content', 'div.content'])
        if main_content:
            content = str(main_content)
        else:
            body = soup.find('body')
            content = str(body) if body else str(soup)

        # Convert to markdown
        markdown_content = md(content)
        
        # Store in database
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

        return markdown_content

    def format_content_with_markdown(self, html_content: str, page_id: int, session) -> str:
        """Format HTML content with markdown, preserving the original order of elements"""
        content_parts = []
        
        # Parse HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Select all headers and paragraphs in order of appearance
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
            try:
                # Get the element name (h1, h2, p, etc.)
                tag_name = element.name

                # Handle headers
                if tag_name.startswith('h'):
                    level = int(tag_name[1])  # get number from h1, h2, etc.
                else:
                    level = 0

                text = element.get_text()
                if text:
                    text = text.strip()
                    content_parts.append(f"{'#' * level} {text}\n\n")

            except Exception as e:
                print(f"Error processing element {element}: {str(e)}")

        content = "".join(content_parts)

        markdown_page = session.query(MarkdownPage).filter(MarkdownPage.scraped_page_id == page_id).first()

        if markdown_page:
            markdown_page.body_md = content
        else:
            markdown_page = MarkdownPage(scraped_page_id=page_id, body_md=content)
            session.add(markdown_page)

        return content

    def process_all_pages(self):
        """Process all HTML pages from database"""
        with session_scope() as session:
            # Query ScrapedPage records with HTML content
            pages = session.query(ScrapedPage).all()

            for page in pages:

                try:
                    html_content = page.response_body.decode("utf-8")

                    self.convert_html_to_markdown(html_content, page.id, session)
                    
                    #self.format_content_with_markdown(html_content, page.id, session)
                except Exception as e:
                    print(f"Error converting page {page.id}: {str(e)}")


