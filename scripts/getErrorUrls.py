from sqlalchemy import text
from app.repository.db import session_scope, Database
from app.repository.models import NonStandardStatusCode

class GetErrorUrls:
    def __init__(self, db: Database):
        self.db = db

    def populate_non_standard_status_codes(self):
        query = """
        SELECT url, response_status_code
        FROM scraped_pages
        WHERE response_status_code <> 200
        AND response_status_code <> 404;
        """
        
        with session_scope() as session:
            # Clean existing data
            session.query(NonStandardStatusCode).delete()
            
            # Execute query and get results
            results = session.execute(text(query))
            
            # Create NonStandardStatusCode objects
            for row in results:
                status_code = NonStandardStatusCode(
                    url=row.url,
                    status_code=row.response_status_code
                )
                session.add(status_code)
            
            session.commit()
            print("Non-standard status codes have been saved to the database")


