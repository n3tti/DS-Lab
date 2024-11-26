from sqlalchemy import text
from app.repository.db import session_scope
import os

def export_markdown_files():
    # Create output directory if it doesn't exist
    output_dir = "exported_markdown"
    os.makedirs(output_dir, exist_ok=True)
    
    query = """
    SELECT s.id as page_id, s.url, m.body_md 
    FROM md_pages m 
    JOIN scraped_pages s ON m.scraped_page_id = s.id
    --WHERE s.id = 3
    LIMIT 50;
    """
    
    with session_scope() as session:
        results = session.execute(text(query))
        
        for row in results:
            page_id = row.page_id
            url = row.url
            markdown_content = row.body_md
            
            # Create filename using page_id
            filename = f"{output_dir}/page_{page_id}.md"
            
            # Add URL as a comment at the top of the file
            content_with_url = f"""<!--
                                Source URL: {url}
                                Page ID: {page_id}
                                -->

                                {markdown_content}"""
            
            # Write content to file
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content_with_url)
            
            print(f"Exported markdown for page {page_id}: {url}")

