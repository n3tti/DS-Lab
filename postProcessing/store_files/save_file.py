'''
Save a downloaded a file fom url, add its filename to the database. Filename correspond to the hash of the url.
'''

from app.repository.db import db

from app.repository.models import FileStorage
import hashlib
from sqlalchemy.exc import IntegrityError
from app.config import SAVE_DOWNLOADED_FILE

SAVE_FILE_FOLDER = SAVE_DOWNLOADED_FILE


def hash_url(url: str) -> str:
    return hashlib.md5(url.encode("utf-8")).hexdigest()


def save_downloaded_file(link_id, url, extension, content):
    try:   
        if not url.lower().endswith(f".{extension}"):
            print("Extension did not match.")
            return False 

        hash_file = hash_url(url)
        file_path = f"{SAVE_FILE_FOLDER}/{hash_file}.{extension}"

        with open(file_path, "wb") as file:
                file.write(content)

        file_storage = FileStorage(link_id=link_id, url=url, extension=extension, filename=hash_file)
        db_check = db.create_file_storage(file_storage)
        if not db_check:
            print("Failed to write to database.")
        return db_check 
    except Exception as e:
        if isinstance(e,IntegrityError):
            print("Did not write the PDF, because of duplicates.")
        else:
            print(f"Error occured : {e}.")
        return False
    

