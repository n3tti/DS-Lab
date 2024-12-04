"""
Run and outputs the results of exemple-queries provided in README.md
 
"""
import sqlite3
import json

def write(output_file, text, query_num):
    with open(output_file, "a") as f:
            f.write("\n")
            f.write(f"---- Query {query_num} ----\n")
            f.write(text)

def query1(cursor, output_file):
    #  Given a page, get the same pages in different languages.
    
    # Get a page for the exemple 
    id = 1
    id_url_query = f"SELECT url FROM scraped_pages WHERE id == {id} LIMIT 1"
    cursor.execute(id_url_query)
    url = cursor.fetchone()[0]

    # Query
    other_id_query = f"SELECT cousin_urls_dict FROM scraped_pages WHERE id == {id} limit 1"
    cursor.execute(other_id_query)
    dic_str = cursor.fetchone()[0]
    dic = json.loads(dic_str)
    formatted = f"Cousin pages of {url} :"
    for key, val in dic.items():
        formatted += f"\n    {key} : {val}"
    write(output_file, formatted, 1)
        

def query4(cursor, output_file): 
    # Get all the url that are referenced by a certain page.

    # Get a page for the exemple 
    id = 17
    id_url_query = f"SELECT url FROM scraped_pages WHERE id == {id} LIMIT 1"
    cursor.execute(id_url_query)
    url = cursor.fetchone()[0]

    # Query
    child_id_query = f"SELECT DISTINCT(child_url) FROM child_parent_links WHERE parent_id = {id}"
    cursor.execute(child_id_query)
    results = cursor.fetchall()
    formatted = f"Child urls of {url} :"
    for row in results:
        formatted += "\n    " + row[0]
    write(output_file, formatted, 4)


def query5(cursor, output_file):
    # Get all pages that reference a certain page.

    # Get a page for the exemple 
    id = 3
    id_url_query = f"SELECT url FROM scraped_pages WHERE id == {id} LIMIT 1"
    cursor.execute(id_url_query)
    url = cursor.fetchone()[0]

    # Query
    parent_id_query = f"SELECT DISTINCT(parent_id) FROM child_parent_links WHERE child_url = '{url}'"
    cursor.execute(parent_id_query)
    results = cursor.fetchall()
    formatted = f"Parents urls of {url} :"
    for row in results:
        id_url_query = f"SELECT url FROM scraped_pages WHERE id == {row[0]} LIMIT 1"
        cursor.execute(id_url_query)
        url = cursor.fetchone()[0]
        formatted += "\n    " + url
    write(output_file, formatted, 5)

def query6(cursor, output_file):
    # Get all referenced pdfs urls from a certain page.

    # Get a page for the exemple 
    id = 22
    id_url_query = f"SELECT url FROM scraped_pages WHERE id == {id} LIMIT 1"
    cursor.execute(id_url_query)
    url = cursor.fetchone()[0]

    # Query
    pdf_url_query = f"SELECT DISTINCT(url) FROM pdf_links WHERE scraped_page_id = '{id}'"
    cursor.execute(pdf_url_query)
    results = cursor.fetchall()
    formatted = f"PDFs referenced by {url} :"
    for row in results:
            formatted += f"\n {row[0]}"
    write(output_file, formatted, 6)

def query7(cursor, output_file):
    # Given pdf url, get the translated pdf in all other languages available. 

    # Get a pdf for the exemple 
    id = 612
    id_url_query = f"SELECT url FROM pdf_links WHERE id == {id} LIMIT 1"
    cursor.execute(id_url_query)
    url = cursor.fetchone()[0]

    # Query
    scraped_page_id = f"SELECT DISTINCT(scraped_page_id) FROM pdf_links WHERE url = '{url}'"
    cursor.execute(scraped_page_id)
    id = cursor.fetchone()[0]
    # get cousin pages
    other_id_query = f"SELECT cousin_urls_dict FROM scraped_pages WHERE id == {id} limit 1"
    cursor.execute(other_id_query)
    dic_str = cursor.fetchone()
    print(dic_str[0])
    dic = json.loads(dic_str[0])
    for key, val in dic.items():
        q =  f"SELECT id FROM scraped_pages WHERE url == '{val}' "
        cursor.execute(q)
        id = cursor.fetchone()[0]
        q =  f"SELECT DISTINCT(url) FROM pdf_links WHERE scraped_page_id == {id}"
        cursor.execute(q)
        pdfs = cursor.fetchall()
        print(pdfs)
    # implement something to match the pdf, ex, same metadata or something
         




if __name__ == "__main__":

    database_file = "C:/Users/eroma/Desktop/Master/MA3/DSL_git/DS-Lab/database/production_subset.db"
    output_file = "./exemple_queries.txt"

    try:
        # Connect to the database
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        
        query1(cursor, output_file)
        query4(cursor, output_file)
        query5(cursor, output_file)
        query6(cursor, output_file)
        query7(cursor, output_file)
        query8(cursor, output_file)



    except sqlite3.Error as e:
        print(f"Error: {e}")
    
