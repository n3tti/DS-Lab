from app.repository.db import db
from simhash import Simhash
import re
import requests
from app.repository.models import PDFLink, PDFMetadata, LinkStatusEnum
from app.repository.db import db
from urllib.parse import urlparse
from multiprocessing import Pool, cpu_count, Value, Lock
import time

ROW_PER_READ = 100
NGRAMS = 3


# Hash == '1' stands for null content or empty content. Hash == '0' stands for processing hash.

def get_features(s):
    width = NGRAMS
    s = s.lower()
    s = re.sub(r"[^\w]+", "", s)
    return [s[i : i + width] for i in range(max(len(s) - width + 1, 1))]


def get_hash(text):
    return str(Simhash(get_features(text)).value)

def compute_simhash(rows):
    for row in rows:
        hash = '1'
        text = row.content_formatted_with_markdown
        if not (text == None or len(text) == 0):
            hash = get_hash(text)
        querydb(2, [row.id, hash])

def retry_on_exception(max_retries=5, delay=0.1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                    else:
                        raise e
        return wrapper
    return decorator


@retry_on_exception(max_retries=5, delay=0.1)
def querydb(code, args):
    if code == 1:
        return db.get_none_hash(args[0])
    if code == 2:
        return db.update_hash(args[0], args[1])

def sim():
    rows = querydb(1, [ROW_PER_READ])
    print("fetched")
    # Use a multiprocessing Pool to process PDFs in parallel
    with Pool(processes=50) as pool:
        pool.map(compute_simhash, rows)


if __name__ == "__main__":
    for i in range(100):
        sim()
