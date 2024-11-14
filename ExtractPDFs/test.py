import pymupdf
from pprint import pprint
import pymupdf4llm
import json

# Write the text to some file in UTF8-encoding
import pathlib


def process_pdf(pdf_name):
    md_text = pymupdf4llm.to_markdown("./%s.pdf" % (pdf_name))
    pathlib.Path("./%s.md" % (pdf_name)).write_bytes(md_text.encode())


    doc = pymupdf.open("./%s.pdf" %(pdf_name))
    if doc.is_encrypted and doc.needs_pass:
        print("Protected and encrypted")
        return

    # metadata
    metadata = doc.metadata
    metadata_dic = {"title" : metadata["title"], "author": metadata["author"], "subject": metadata["subject"], 
                    "keywords": metadata["keywords"], "creationDate": metadata["creationDate"], "modDate": metadata["modDate"],
                    "links" : [], "images" : []}
    
    toc = doc.get_toc() #table of content


    for page_index in range(len(doc)): # iterate over pdf pages
        page = doc[page_index] # get the page

        out = open("output.txt", "wb") # create a text output
        text = page.get_text().encode("utf8") # get plain text (is in UTF-8)
        out.write(text) # write text of page
        out.write(bytes((12,))) # write page delimiter (form feed 0x0C)
        out.close()

        image_list = page.get_images()
        if image_list:
            for image_index, img in enumerate(image_list, start=1): # enumerate the image list
                xref = img[0] # get the XREF of the image
                pix = pymupdf.Pixmap(doc, xref) # create a Pixmap
                if pix.n - pix.alpha > 3: # CMYK: convert to RGB first
                    pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
                img_name = "%s_page_%s-image_%s.png" % (pdf_name, page_index, image_index)
                metadata_dic["images"].append(img_name)
                pix.save(img_name) # save the image as png
                pix = None

        # tabs = page.find_tables()
        # if tabs.tables:  # at least one table found?
        #     pprint(tabs[0].extract()) 
           
        link = page.first_link 
        while link:
            if link.is_external:
                metadata_dic["links"].append(link.uri)
            link = link.next 

    metadata_dic
    line = json.dumps(metadata_dic)
    meta = open("./meta.json", "w")
    meta.write(line)
    doc.close()




if __name__ == "__main__":

    process_pdf("89940")