import html2text
import requests

from app.logs import logger

if __name__ == "__main__":
    logger.debug("This is a debug message: Processing pdfs... 1")
    logger.info("This is an info message: Processing pdfs... 2")

    url = "https://www.efv.admin.ch/efv/fr/home/efv/erechnung/aktuell.html"
    response = requests.get(url)

    html_content = response.text

    h = html2text.HTML2Text()

    # Ignore links and images if desired
    h.ignore_links = True
    h.ignore_images = True

    # Convert to Markdown
    markdown_content = h.handle(html_content)

    # Save to a Markdown file
    with open("output.md", "w", encoding="utf-8") as md_file:
        md_file.write(markdown_content)
