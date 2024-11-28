import requests
from bs4 import BeautifulSoup


url = "https://www.bit.admin.ch/en/sgc-en"

response = requests.get(url)
response.raise_for_status()


soup = BeautifulSoup(response.text, "html.parser")
formatted_html = soup.prettify()
with open("formatted_output.html", "w", encoding="utf-8") as f:
    f.write(formatted_html)


##########################################################################################
from html2text import HTML2Text


# Configure HTML2Text
converter = HTML2Text()
converter.ignore_links = False    # Include links in the output
converter.ignore_images = False   # Include image placeholders
converter.ignore_tables = False   # Include tables
converter.protect_links = True    # Prevent splitting of links

# Convert HTML to Markdown
print("##########################################################################################")
print(converter.handle(response.text))
print()
print()
print()
print()
print()
print()
print()
print()
print()



##########################################################################################
from markdownify import markdownify as md

markdown_content = md(response.text)
print("##########################################################################################")
print(markdown_content)
print()
print()
print()
print()
print()
print()
print()
print()
print()


##########################################################################################
# Slightly adapted

# from bs4 import BeautifulSoup
def format_content_with_markdown(file_path):
    """Format content with markdown from an HTML file, preserving the original order of elements"""
    content_parts = []

    # Read the HTML file
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

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

input_file = "/Users/saschatran/Downloads/output.html"

formatted_markdown = format_content_with_markdown(input_file)
print("##########################################################################################")
print(formatted_markdown)
print()
print()
print()
print()
print()
print()
print()
print()
print()

with open("output_w_js.md", "w", encoding="utf-8") as f:
    f.write(formatted_markdown)

from bs4 import BeautifulSoup
from html2text import HTML2Text


# First part - formatting and saving HTML
def format_html_file(input_file_path, output_file_path="formatted_output.html"):
    # Read the input HTML file
    with open(input_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Parse and prettify
    soup = BeautifulSoup(html_content, "html.parser")
    formatted_html = soup.prettify()

    # Save formatted HTML
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(formatted_html)


# Second part - converting to markdown
def convert_to_markdown(input_file_path):
    # Read the HTML file
    with open(input_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Configure HTML2Text
    converter = HTML2Text()
    converter.ignore_links = False  # Include links in the output
    converter.ignore_images = False  # Include image placeholders
    converter.ignore_tables = False  # Include tables
    converter.protect_links = True  # Prevent splitting of links

    # Convert HTML to Markdown
    print("##########################################################################################")
    print()
    print("\n" * 9)  # This creates the 9 empty lines as in your original code
    return converter.handle(html_content)

format_html_file(input_file)
m = convert_to_markdown(input_file)

with open("output_w_js_otherversion.md", "w", encoding="utf-8") as f:
    f.write(m)