from queries.queries_base import get_cousin_id, get_translated_pdfs

def pdf_dataset(id, output_file, split = True, split_length = 200, split_padding = 0, add_order = False, add_metadata = False, metadata_fields = None):

    # from one pdf url or id, get cousins pdf, and split according to lenghtmax and padding
    # like {en : "text", fr : "text" ....}
    # result = []
    # get_translated_pdfs(id)

    # to_jsonl(result)
    pass



def page_dataset(url_or_id, split = True, split_length = 200, split_padding = 0, add_order = False, add_metadata = False, metadata_fields = None):
    pass



