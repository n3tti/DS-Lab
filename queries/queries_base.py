
import json
from simhash import SimhashIndex, Simhash
import re

def get_cousin_url(cursor, id):
    #  Given a page id, get the same pages url's in different languages.
    other_id_query = f"SELECT cousin_urls_dict, response_metadata_lang, url FROM scraped_pages WHERE id == {id} LIMIT 1"
    cursor.execute(other_id_query)
    result = cursor.fetchone()
    if result == None:
        return []
    dic_str, lang, url = result
    if dic_str == None:
        return []
    dic = json.loads(dic_str)
    res = []
    for key, val in dic.items():
        res.append({"lang": key, "url": val})
    return res

def get_cousin_id(cursor, id):
    #  Given a page id, get the same pages id's in different languages.
    other_id_query = f"SELECT cousin_urls_dict, response_metadata_lang FROM scraped_pages WHERE id == {id} LIMIT 1"
    cursor.execute(other_id_query)
    result = cursor.fetchone()
    if result == None:
        return []
    dic_str, lang = result
    if dic_str == None:
        return []
    r = []
    for key,val in json.loads(dic_str).items():
        cousin_id = f"SELECT id FROM scraped_pages WHERE url = '{val}' LIMIT 1"
        cursor.execute(cousin_id)
        result = cursor.fetchone()
        if result != None:
            r.append({"lang" : key, "id" : result[0]})
    return r

def get_childs_id(cursor, id): 
    # Get all the id of the url that are referenced by a certain page.
    child_url_query = f"SELECT DISTINCT(child_url) FROM child_parent_links WHERE parent_id = {id}"
    cursor.execute(child_url_query)
    results = cursor.fetchall()
    if results == None:
        return []
    r = []
    for row in results:
        child_id_query = f"SELECT id FROM scraped_pages WHERE url = '{row[0]}' LIMIT 1"
        cursor.execute(child_id_query)
        result = cursor.fetchone()
        if result != None:
            r.append({"parent_id" : id, "child_id" : result[0]})
    return r

def get_childs_url(cursor, id): 
    # Get all the url that are referenced by a certain page.
    child_url_query = f"SELECT DISTINCT(child_url) FROM child_parent_links WHERE parent_id = {id}"
    cursor.execute(child_url_query)
    results = cursor.fetchall()
    if results == None:
        return []
    return [{"parent_id": id, "child_url" : row[0]} for row in results]


def get_parent_url(cursor, id):
    # Get all pages url's that reference a certain page
    url_query = f"SELECT url FROM scraped_pages WHERE id = {id}"
    cursor.execute(url_query)
    url = cursor.fetchone()
    if url == None:
        return []
    parent_query = f"SELECT DISTINCT(parent_id) FROM child_parent_links WHERE child_url = '{url[0]}'"
    cursor.execute(parent_query)
    parents = cursor.fetchall()
    if parents == None:
        return []
    res = []
    for parent in parents:
        p_id = parent[0]
        url_query = f"SELECT url FROM scraped_pages WHERE id = {p_id}"
        cursor.execute(url_query)
        url = cursor.fetchone()
        if url != None:
            res.append({"parent_url": url[0], "child_id" : id})
    return res


def get_parent_id(cursor, id):
    # Get all pages id's that reference a certain page
    url_query = f"SELECT url FROM scraped_pages WHERE id = {id}"
    cursor.execute(url_query)
    url = cursor.fetchone()
    if url == None:
        return []
    parent_query = f"SELECT DISTINCT(parent_id) FROM child_parent_links WHERE child_url = '{url[0]}'"
    cursor.execute(parent_query)
    results = cursor.fetchall()
    if results == None:
        return []
    return [{"parent_id": row[0], "child_id" : id} for row in results]

def get_referenced_pdfs_from_page(cursor, id):
    child_url_query = f"SELECT DISTINCT(child_url) FROM child_parent_links WHERE parent_id = {id}"
    cursor.execute(child_url_query)
    results = cursor.fetchall()
    if results == None:
        return []
    res = []
    for url in results:
        if url[0].endswith(".pdf"):
            res.append({"parent_id": id, "pdf_url" : url[0]})
    return res
    

def get_pdf_md(cursor, url):
    # Get Markdown text content extracted from a specific PDF.
    pdf_md_query = f"SELECT md_text FROM pdf_links WHERE url = '{url}' LIMIT 1"
    cursor.execute(pdf_md_query)
    result = cursor.fetchone()
    if result is None:
        return []
    return [{"url": url, "md_text": result[0]}]


def get_stored_file_filename_from_url(cursor, url):
    # Get the filename (without extension) of a stored ressource (ex: png, pdf...) from url
    filename_query = f"SELECT filename FROM file_storage WHERE url = '{url}' LIMIT 1"
    cursor.execute(filename_query)
    result = cursor.fetchone()
    if result is None:
        return []
    return [{"url": url, "filename": result[0]}]


def get_simhash_distance(cursor, id1, id2):
    # Get the simhash distance between 2 pages, given their id's
    query = f"SELECT response_metadata_content_hash FROM scraped_pages WHERE id IN ({id1}, {id2})"
    cursor.execute(query)
    results = cursor.fetchall()
    if results == None:
        return []
    if len(results) != 2 or any(r[0] is None for r in results) or any((r[0] == '0' or r[0] == '1' or  r[0] == '') for r in results):
        return []
    hash1 = int(results[0][0])
    hash2 = int(results[1][0])
    xor_result = hash1 ^ hash2
    distance = bin(xor_result).count("1")
    return [{"id_1" : id1, "id_2" : id2, "distance" : distance}]

