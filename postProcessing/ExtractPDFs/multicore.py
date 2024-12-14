import requests
from app.repository.models import PDFMetadata, LinkStatusEnum
from app.repository.db import db

from postProcessing.store_files.save_file import save_downloaded_file

import pymupdf4llm
import pymupdf
from urllib.parse import urlparse
from multiprocessing import Pool, cpu_count, Value, Lock
import time

ROW_PER_READ = 50000
processed_count = Value('i', 0)  # Integer counter
lock = Lock()

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
        return db.get_unprocessed_pdf(args[0])
    if code == 2:
        return save_downloaded_file(args[0], args[1], "pdf", args[2])
    if code == 3:
        return db.add_processed_pdf(args[0], args[1], args[2], args[3], args[4], args[5])


def validate_url(url):
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "https://" + url
    elif parsed.scheme not in ["http", "https"]:
        url = url.replace(parsed.scheme, "https", 1)
    return url


def try_open(content):
    try:
        return pymupdf.Document(stream=content)
    except Exception:
        print("Failed to open doc.")
        return None
def try_read(doc):
    try:
        return pymupdf4llm.to_markdown(doc, show_progress=False)
    except Exception:
        print("Failed to read.")
        return None

def process_pdf(row):
    global processed_count
    url = validate_url(row.url)
    try:
        response = requests.get(url)
    except Exception as e:
        print(f"Failed to download: {e}")
        querydb(3, [row.id, None, None, None, None, LinkStatusEnum.FAILED])
        return

    if response.status_code == 200 and response.content:
        downloaded = querydb(2, [row.id, row.url, response.content])
        if downloaded:
            doc = try_open(response.content)
            if not doc or (doc.is_encrypted and doc.needs_pass):
                print("PDF is encrypted or empty.")
                querydb(3, [row.id, None, None, None, None, LinkStatusEnum.DOWNLOADED])
            else:
                metadata = doc.metadata
                metadata_obj = PDFMetadata(
                    title=metadata.get("title"),
                    author=metadata.get("author"),
                    subject=metadata.get("subject"),
                    keywords=metadata.get("keywords"),
                    creationDate=metadata.get("creationDate"),
                    modDate=metadata.get("modDate"),
                )
                md_text = try_read(doc)
                if md_text== None:
                    querydb(3, [row.id, None, None, None, None, LinkStatusEnum.FAILED])
                else:
                    querydb(3, [row.id, metadata_obj, md_text, None, None, LinkStatusEnum.PROCESSED])
        else:
            print(f"Failed to save PDF.")
            querydb(3, [row.id, None, None, None, None, LinkStatusEnum.FAILED])
    else:
        print(f"Failed to download, status code: {response.status_code}")
        querydb(3, [row.id, None, None, None, None, LinkStatusEnum.FAILED])
    with lock:
        processed_count.value += 1
        print(processed_count.value)

def parsePDFs():
    print("fetch")
    rows = querydb(1, [ROW_PER_READ])
    print("feteched")
    # Use a multiprocessing Pool to process PDFs in parallel
    with Pool(processes=50) as pool:
        pool.map(process_pdf, rows)


if __name__ == "__main__":
    for i in range(100):
        parsePDFs()

