# Query Examples on the Dataset

This document provides examples of queries applied to the dataset. 
The code for each query can be found in query_base.py, and exemples of each query are available in exemple_queries.py


## Given a page, get pages that are the translated version of this page.
SQL query : \
    get_cousin_url(exemple_id = 1) \
Result : \
{'lang': 'de', 'url': 'https://www.bk.admin.ch/bk/de/home.html'} \
{'lang': 'en', 'url': 'https://www.bk.admin.ch/bk/en/home.html'} \
{'lang': 'it', 'url': 'https://www.bk.admin.ch/bk/it/home.html'} \
{'lang': 'rm', 'url': 'https://www.bk.admin.ch/bk/rm/home.html'} \
{'lang': 'fr', 'url': 'https://www.bk.admin.ch/bk/fr/home.html'} \


## Given a page, get pages referenced by this page.
SQL query : \
    get_childs_url(exemple_id = 1) \
Result : \
{'parent_id': 1, 'child_url': 'https://digital.swiss/de/'} \
{'parent_id': 1, 'child_url': 'https://www.admin.ch/gov/de/start/rechtliches.html'} \
{'parent_id': 1, 'child_url': 'https://www.bk.admin.ch/bk/de/home.html'} \
{'parent_id': 1, 'child_url': 'https://www.bk.admin.ch/bk/de/home.html#content'} \
{'parent_id': 1, 'child_url': 'https://www.bk.admin.ch/bk/de/home.html#main-navigation'} \
{'parent_id': 1, 'child_url': 'https://www.bk.admin.ch/bk/de/home.html#mf_glossary_tab'} \
 ... 


## Given a page, get pages that reference this page.
SQL query : \
    get_parent_url(exemple_id = 3) \
Result : \
{'parent_url': 'https://www.bk.admin.ch/bk/de/home.html', 'child_id': 3} \
{'parent_url': 'https://www.uvek.admin.ch/uvek/de/home.html', 'child_id': 3} \
{'parent_url': 'https://www.admin.ch/gov/de/start/service/kontakt.html', 'child_id': 3} \
{'parent_url': 'https://www.admin.ch/gov/de/start/bundespraesidium.html', 'child_id': 3} \
{'parent_url': 'https://www.admin.ch/gov/de/start/bundesrat.html', 'child_id': 3} \
 ...


## Given a page, get url of pdfs referenced by that page.
SQL query : \
    get_referenced_pdfs_from_page(exemple_id = 22) \
Result : \
TODO, run exemple query on full db


## Given a pdf, get pdf url's that are the translation of this pdfs.
SQL query : \
    TODO
Result : \
TODO, run exemple query on full db


## Given the url of a stored ressource, get the its filename.
SQL query : \
    TODO
Result : \
TODO, run exemple query on full db


## Given two pages, get their simhash distance.
SQL query : \
    get_simhash_distance(exemple_id1 = 1, exemple_id2 = 2) \
Result : \
TODO, run exemple query on full db


## Given a page, get pages with simhash distance below a threshord.
SQL query : \
    get_similar_pages(exemple_id1 = 1) \
Result : \
TODO, run exemple query on full db


