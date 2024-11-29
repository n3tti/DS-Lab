from playwright.sync_api import sync_playwright
import time


#from app.repository.db import db
#from app.repository.models import ScrapedPage, PageStatusEnum

def access_url_with_retries(url, max_retries=3, delay=2):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt + 1} to access {url}")
                page.goto(url)
                # Check if the page loaded successfully
                if page.title():

                    print(f"Successfully accessed {url}")
                    # Save or update the page information to the database
                    #save_or_update_page_in_db(url, page)
                    save_html_file(page)
                    break
            except Exception as e:
                print(f"Error accessing {url}: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
        else:
            print(f"Failed to access {url} after {max_retries} attempts.")
        
        page.close()
        browser.close()

def save_html_file(page): 
    with open("recrawl_js.html", "w") as file:
        file.write(page.content())

def save_or_update_page_in_db(url, page):
    existing_page = db.get_scraped_page(url=url)
    
    if existing_page:
        # Update existing page
        existing_page.response_status_code = 200  # Assuming success
        existing_page.response_text = page.content()  # Get the page content
        existing_page.response_content_type = page.evaluate("() => document.contentType")  # Get content type
        db.update_scraped_page_status(existing_page.id, PageStatusEnum.REVISITED)  # Update status if needed
    else:
        # Create new page entry
        new_page = ScrapedPage(
            url=url,
            response_status_code=200,  # Assuming success
            response_text=page.content(),  # Get the page content
            response_content_type=page.evaluate("() => document.contentType"),  # Get content type
            # Add other fields as necessary
        )
        db.create_scraped_page(new_page)  # Save to the database

# Example usage
url_to_access = "https://www.fedlex.admin.ch/eli/cc/1960/525_569_555/de"
access_url_with_retries(url_to_access)