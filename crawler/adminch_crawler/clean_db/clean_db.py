import json
from adminch_crawler.config import (
    PARENTS_DIR,
    PDF_FILE
)



def pdf_clean():
    data = json.loads(PDF_FILE)
