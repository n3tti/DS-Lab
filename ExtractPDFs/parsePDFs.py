import requests
from app.repository.models import PDFLink, PDFMetadata, LinkStatusEnum
from app.repository.db import db

from store_files.save_file import save_downloaded_file
import pymupdf4llm
import pymupdf


ROW_PER_READ = 10

def parsePDFs():

    rows = db.get_unprocessed_pdf(ROW_PER_READ)

    for row in rows:

        response = requests.get(row.url)
        if response.status_code == 200 and response.content != None:
            downloaded = save_downloaded_file(row.id, row.url, "pdf", response.content)
            if downloaded:
                doc = pymupdf.Document(stream=response.content)
                if doc == None or (doc.is_encrypted and doc.needs_pass):
                    print("PDF is encrypted or empty.")
                    db.add_processed_pdf(row.id, None, None, None, None, LinkStatusEnum.DOWNLOADED)
                else:
                    metadata = doc.metadata
                    metadata_obj = PDFMetadata(title = metadata["title"], author =  metadata["author"], \
                            subject = metadata["subject"], keywords = metadata["keywords"],\
                            creationDate = metadata["creationDate"], modDate = metadata["modDate"])
                    md_text = pymupdf4llm.to_markdown(doc)
                    db.add_processed_pdf(row.id, metadata_obj, md_text, None, None, LinkStatusEnum.PROCESSED)
            else:
                print("PDF was downloaded, but failed to save it.")
                db.add_processed_pdf(row.id, None, None, None, None, LinkStatusEnum.FAILED)
        else:
            print(f"Unable to download the PDF, status = {response.status_code}.")
            db.add_processed_pdf(row.id, None, None, None, None, LinkStatusEnum.FAILED)


def parse():
    while True:
        parsePDFs()


if __name__ == "__main__":
    parse()


       
