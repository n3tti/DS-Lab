import BeautifulSoup

from app.logs import logger
from app.repository.db import db

def convert_to_md(html):
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Select all headers and paragraphs in order of appearance
    for element in soup.select("h1, h2, h3, h4, h5, h6, p"):
        # Get the element name (h1, h2, p, etc.)
        tag_name = element.name

        # Handle headers
        if tag_name.startswith("h"):
            level = int(tag_name[1])  # get number from h1, h2, etc.
        else:
            level = 0

        text = element.get_text()
        if text:
            text = text.strip()
            content_parts.append(f"{'#' * level} {text}\n\n")

    return "".join(content_parts)

if __name__ == "__main__":
    for unconverted_scraped_page_id in db.get_scraped_page_unconverted_ids():
        logger.info(f"Converting scraped page with id: {unconverted_scraped_page_id} to MarkDown")

        unconverted_scraped_page = db.get_scraped_page_by_id(unconverted_scraped_page_id)

        html_content = unconverted_scraped_page.response_text

        markdown_content = convert_to_md(html_content)

        db.update_scraped_page_with_markdown_content(unconverted_scraped_page_id, markdown_content)