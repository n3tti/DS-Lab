import html2text

from app.logs import logger
from app.repository.db import db

if __name__ == "__main__":
    for unconverted_scraped_page_id in db.get_scraped_page_unconverted_to_md_ids():
        logger.info(f"Converting scraped page with id: {unconverted_scraped_page_id} to MarkDown")

        unconverted_scraped_page = db.get_scraped_page_by_id(unconverted_scraped_page_id)

        html_content = unconverted_scraped_page.response_text

        converter = html2text.HTML2Text()

        converter.ignore_links = True    # Include links in the output
        converter.ignore_images = True   # Include image placeholders
        converter.ignore_tables = False   # Include tablese
        converter.protect_links = True    # Prevent splitting of links

        markdown_content = converter.handle(html_content)

        db.update_scraped_page_with_markdown_content(unconverted_scraped_page_id, markdown_content)
