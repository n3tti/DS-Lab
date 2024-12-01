'''

todo

'''

from app.repository.db import db
from app.repository.models import FileStorage
import hashlib


SAVE_FILE_FOLDER = "C:/Users/eroma/Desktop/Master/MA3/DSL_git/DS-Lab/samplefolder/"


def hash_url(url: str) -> str:
    return hashlib.md5(url.encode("utf-8")).hexdigest()


def save_downloaded_file(link_id, url, extension, content):
    try:   
        if not url.lower().endswith(f".{extension}"):
            return False 

        hash_file = hash_url(url)
        file_path = f"{SAVE_FILE_FOLDER}/{hash_file}.{extension}"

        with open(file_path, "wb") as file:
                file.write(content)

        file_storage = FileStorage(link_id=link_id, url=url, extension=extension, filename=hash_file)
        db_check = db.create_file_storage(file_storage)
        return db_check 
    except:
        return False
    

