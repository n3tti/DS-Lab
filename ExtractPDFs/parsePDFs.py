
from app.repository.db import db
from queue import Queue
import requests
from app.repository.models import PDFLink, LinkStatusEnum, PDFMetadata

import pymupdf4llm
import pymupdf


# In the db, look for pdfs that are not yet processed
def get_unprocessed_pdf_url() -> Queue[PDFLink]:
    queue = Queue()
    pdf_obj_list = db.get_pdf_from_status([LinkStatusEnum.DISCOVERED, LinkStatusEnum.FAILED, LinkStatusEnum.DOWNLOADED]) 
    for pdf_obj in pdf_obj_list:
        # TODO update status as processing ?
        queue.put(pdf_obj) 
    return queue

def download_and_get_pdf_data(pdf : PDFLink):
    doc = None
    r = requests.get(pdf.url)
    if r.status_code == 200:
        data = r.content
        doc = pymupdf.Document(stream=data)

    return doc, status_code


def parse_pdf(doc):
    if doc.is_encrypted and doc.needs_pass:
        return None, None, None, None
    metadata = doc.metadata
    metadata_obj = PDFMetadata(title = metadata["title"], author =  metadata["author"], \
                    subject = metadata["subject"], keywords = metadata["keywords"],\
                    creationDate = metadata["creationDate"], modDate = metadata["modDate"])
  
    # for page_index in range(len(doc)):  # iterate over pdf pages
    #     page = doc[page_index]  # get the page
    #     image_list = page.get_images()
    #     if image_list:
    #         for image_index, img in enumerate(image_list, start=1):  # enumerate the image list
    #             xref = img[0]  # get the XREF of the image
    #             pix = pymupdf.Pixmap(doc, xref)  # create a Pixmap
    #             if pix.n - pix.alpha > 3:  # CMYK: convert to RGB first
    #                 pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    #             img_name = "%s_page_%s-image_%s.png" % (pdf_name, page_index, image_index)
    #             metadata_dic["images"].append(img_name)
    #             pix.save(img_name)  # save the image as png
    #             pix = None

    #     link = page.first_link
    #     while link:
    #         if link.is_external:
    #             metadata_dic["links"].append(link.uri)
    #         link = link.next

    md_text = pymupdf4llm.to_markdown(doc)

    return metadata_obj, md_text, None, None



if __name__ == "__main__":

    url_queue = get_unprocessed_pdf_url()
    while not url_queue.qsize() == 0:
        pdf_link = url_queue.pop()
        doc, status_code = download_and_get_pdf_data(pdf_link)
        md = None
        if status_code == 200 and doc != None:
            metadata, md, links, images = parse_pdf(doc)
            db.add_pdf_md(pdf_link.id, metadata, md, links, images)
        else:
            db.update_pdf_status(pdf_link.id, LinkStatusEnum.FAILED)
        

            




