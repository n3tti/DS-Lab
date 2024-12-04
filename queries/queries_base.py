
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


# TODO

def get_similar_pages(cursor, id, threshold):
    pass
#     # Given a page id and a threshold, get similar pages
#     query = "SELECT id, response_metadata_content_hash FROM scraped_pages WHERE response_metadata_content_hash IS NOT NULL"
#     cursor.execute(query)
#     results = cursor.fetchall()
#     if results == None:
#         return []
#     objs = []
#     for row in results:
#         page_id = str(row[0])  
#         simhash_value = int(row[1]) 
#         objs.append((page_id, Simhash(simhash_value)))

#     # Create the Simhash index
#     index = SimhashIndex(objs, k=threshold)
#     new_dup = index.get_near_dups(id)  
#     sim = [{"id" : id}]
#     return index
#     pass





### Get translated PDFs

def get_ngram_numbers(s):
    width = 3
    return [s[i:i + width] for i in range(max(len(s) - width + 1, 1))]

def get_digits(string):
    s = ''
    for char in string:
        if char.isdigit():
            s+=char

def dist(url1, title1, url2, title2):
    dist = 0
    if url1 == url2:
        return dist
    split_url1 = url1.split("/")
    split_url2 = url2.split("/")
    if title1 != None and title1 != '' and title2 != None and title2 != '':
        if title1 == title2:
            return dist
        if any(char.isdigit() for char in title1) and any(char.isdigit() for char in title1):
            a = get_digits(title1)
            b = get_digits(title2)
            if a == b:
                return dist
            dist += Simhash(get_ngram_numbers(a)).distance(Simhash(get_ngram_numbers(b)))
            return dist     
    if len(split_url1) != len(split_url2):
        dist += 50
    len_i = min(len(split_url1), len(split_url2))
    split_url1 = split_url1[:len_i]
    split_url2 = split_url2[:len_i]
    temp = 0
    for i in range(len_i):
        temp += Simhash(get_ngram_numbers(split_url1[i])).distance(Simhash(get_ngram_numbers(split_url2[i])))
    dist += temp/len_i
    return dist
    

def get_translated_pdfs(cursor, url):

    # 1- Get the parent page
    # A pdf can be referenced by different pages, prioritize pages that:
    # - have cousins
    # - reference the less pages
    query = f"SELECT parent_id, COUNT(*) FROM child_parent_links WHERE child_url = '{url}' GROUP BY parent_id"
    cursor.execute(query)
    results = cursor.fetchall()
    if results == None:
        return []
    dic = {}
    for row in results:
        dic[row[1]] = row[0]
    sorted_dic = dict(sorted(dic.items()))
    id = None
    cousins_dic = None
    for key, val in sorted_dic.items():
        q  = f"SELECT cousin_urls_dict FROM scrapaed_pages WHERE id = {val}"
        cursor.execute(q)
        result = cursor.fetchone()
        if id == None and result != None and len(json.loads(result[0])) > 1:
            id = val
            cousins_dic = json.loads(result[0])
    if cousins_dic == None:
        return []
    # Get cousin pages id:

    # 3- Get the referenced pdfs from each cousin page
    for key, val in cousins_dic.items():
        id = ...
        pdf_urls = get_referenced_pdfs_from_page(cursor, id)
        if len(pdf_urls) != 0:
            for row in pdf_urls:
                url = row["url"]



    # 4- For each cousin page, get the most likely pdf
    # same url
    # if title:
    # same title
        # if title contains number : simash
    # if no title:
    # simash on url