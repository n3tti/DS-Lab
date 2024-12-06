from app.repository.db import db
from app.repository.models import ScrapedPage
from app.repository.db import session_scope  # Add this import
import jsonlines

def extract_markdown_to_jsonl(output_file: str):
    data = []
    with session_scope() as session:  # Use session_scope directly
        query = session.query(
            ScrapedPage.id,
            ScrapedPage.content_formatted_with_markdown
        ).filter(
            ScrapedPage.content_formatted_with_markdown.isnot(None)
        )
        
        for page_id, content in query.yield_per(1000):
            if content:  # Skip empty content
                data.append({
                    "id": page_id,
                    "content": content
                })
    
    with jsonlines.open(output_file, mode='w') as writer:
        writer.write_all(data)

if __name__ == '__main__':
    extract_markdown_to_jsonl("output.jsonl")