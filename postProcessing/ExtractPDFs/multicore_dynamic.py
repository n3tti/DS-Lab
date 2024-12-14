from multiprocessing import Pool, cpu_count
import itertools
import time
import requests
from app.repository.models import PDFLink, PDFMetadata, LinkStatusEnum
from app.repository.db import db

from postProcessing.store_files.save_file import save_downloaded_file

import pymupdf4llm
import pymupdf
from urllib.parse import urlparse
from multiprocessing import Pool, cpu_count

ROW_PER_READ = 5000


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
    match code:
        case 1:
            return db.get_unprocessed_pdf(args[0])
        case 2:
            return save_downloaded_file(args[0], args[1], "pdf", args[2])
        case 3:
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
        print("Failed to open doc")
        return None


def process_pdf(row):
    url = validate_url(row.url)
    try:
        response = requests.get(url)
    except Exception as e:
        print(f"Failed to download") #{url}: {e}")
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
                md_text = pymupdf4llm.to_markdown(doc, show_progress=False)
                print(f"Processed")
                querydb(3, [row.id, metadata_obj, md_text, None, None, LinkStatusEnum.PROCESSED])
        else:
            print(f"Failed to save downloaded PDF from")# {url}")
            querydb(3, [row.id, None, None, None, None, LinkStatusEnum.FAILED])
    else:
        print(f"Failed to download, status code: {response.status_code}")
        querydb(3, [row.id, None, None, None, None, LinkStatusEnum.FAILED])




def parsePDFs():
    def row_generator():
        """Generator to fetch and yield rows in chunks."""
        while True:
            rows = querydb(1, [ROW_PER_READ])  # Fetch rows from the database
            if not rows:
                break
            for row in rows:
                yield row

    # Number of worker processes
    num_processes = 40

    # Use Pool and imap_unordered for dynamic assignment
    with Pool(processes=num_processes) as pool:
        # Dynamically feed rows to workers
        for _ in pool.imap_unordered(process_pdf, row_generator()):
            pass  # imap_unordered processes items dynamically

if __name__ == "__main__":
    #while True:
     #   try:
    parsePDFs()
      #  except:
       #     print("----------------------------ERROR ON DB-----------------------------------")
