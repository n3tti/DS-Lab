import requests
from app.repository.models import PDFLink, PDFMetadata, LinkStatusEnum
from app.repository.db import db

from postProcessing.store_files.save_file import save_downloaded_file

import pymupdf4llm
import pymupdf
from urllib.parse import urlparse, urlunparse

ROW_PER_READ = 50


def validate_url(url):
    parsed = urlparse(url)
    if not parsed.scheme:  # If no scheme is provided
        url = "https://" + url  # Default to https
    elif parsed.scheme not in ["http", "https"]:  # If an invalid scheme exists
        url = url.replace(parsed.scheme, "https", 1)
    return url

def try_open(content):
    doc = None
    try:
        doc = pymupdf.Document(stream=content)
    except Exception as e:
        print("Failed to open doc")
    return doc

def try_read(doc):
    md_text = None
    try:
        md_text = pymupdf4llm.to_markdown(doc, show_progress=False)
    except Exception as e:
        print("Failed to read doc")
    return md_text


def querydb(code, args):
    flag = False
    temp = None
    while not flag:
        try:
            if code == 1:
                temp =  db.get_unprocessed_pdf(args[0])
                flag = True
            elif code == 3:
                db.add_processed_pdf(args[0], args[1], args[2], args[3], args[4], args[5])
                flag = True
        except:
            flag = False
    return temp

def parsePDFs():

    rows = querydb(1, [ROW_PER_READ])

    for row in rows:
        url = validate_url(row.url)
        response = None
        flag = True
        try:
            response = requests.get(url)
        except Exception as e:
            flag = False
        if flag and response.status_code == 200 and response.content != None:
            downloaded = save_downloaded_file(row.id, row.url, "pdf", response.content)
            if downloaded:
                doc = try_open(response.content)
                if doc == None or (doc.is_encrypted and doc.needs_pass):
                    print("PDF is encrypted or empty.")
                    querydb(3, [row.id, None, None, None, None, LinkStatusEnum.DOWNLOADED])
                else:
                    metadata = doc.metadata
                    metadata_obj = PDFMetadata(title = metadata["title"], author =  metadata["author"], \
                            subject = metadata["subject"], keywords = metadata["keywords"],\
                            creationDate = metadata["creationDate"], modDate = metadata["modDate"])
                    md_text = try_read(doc)
                    if md_text == None:
                        querydb(3, [row.id, None, None, None, None, LinkStatusEnum.FAILED])
                    else :
                        print("Processed")
                        querydb(3, [row.id, metadata_obj, md_text, None, None, LinkStatusEnum.PROCESSED])
            else:
                print("PDF was downloaded, but failed to save it.")
                querydb(3, [row.id, None, None, None, None, LinkStatusEnum.FAILED])
        else:
            print(f"Unable to download the PDF, status.")
            querydb(3, [row.id, None, None, None, None, LinkStatusEnum.FAILED])


def parse():
    while True:
        parsePDFs()


if __name__ == "__main__":
    parse()
