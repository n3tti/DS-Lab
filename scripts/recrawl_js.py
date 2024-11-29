import os
from app.repository.models import ScrapedPage  # Adjust the model import as necessary
from app.repository.db import Database, session_scope
import requests  # Assuming requests is imported and has a seen attribute
import tempfile


def get_urls_for_rescraping(db: Database):
    # Connect to the database
    with session_scope() as session:
        # Query for pages with a <noscript> tag
        pages = session.query(ScrapedPage).filter(ScrapedPage.response_text.contains('<noscript>')).all()
        
        # Extract URLs and markdown content
        urls_to_rescrape = []
        for page in pages:
            urls_to_rescrape.append({
                'url': page.url,
                'id': page.id  # Assuming you have access to the ID
            })

    # Save the URLs into a text file and remove IDs from requests.seen
    with open('urls_to_rescrape.txt', 'w') as file:
        print("saved urls")
        for entry in urls_to_rescrape:
            file.write(f'"{entry["url"]}",\n')
    
    file_path = '/Users/saschatran/Desktop/Uni gits/DS-Lab/.persistence/jobdir/requests.seen'


    # Create a temporary file
    temp_fd, temp_path = tempfile.mkstemp()

    # Set of IDs to remove from the file
    ids_to_remove = {entry['id'] for entry in urls_to_rescrape}

    # Read from the original file and write to a temporary file only the IDs that should not be removed
    with open(file_path, 'r') as file, os.fdopen(temp_fd, 'w') as temp_file:
        for line in file:
            line = line.strip()
            if line not in ids_to_remove:
                temp_file.write(f'{line}\n')

    # Replace the original file with the updated one
    os.replace(temp_path, file_path)



# "Get all urls that require rescraping due to missing JavaScript rendering"

# !important: adjust pipeline such that when rescraping specific urls, only the relevant new information are replaced
# not a completely new entry

# also don't forget to remove the urls in .persistence
