"""
Run and outputs the results of exemple-queries provided in README.md
 
"""
import sqlite3
import json
from queries_base import get_childs_id, get_childs_url, get_cousin_id, get_cousin_url, get_parent_id, get_pdf_md,\
get_simhash_distance, get_stored_file_filename_from_url, get_translated_pdfs,\
get_similar_pages, get_referenced_pdfs_from_page, get_parent_url


EXEMPLE = [1, 3, "https://www.newsd.admin.ch/newsd/message/attachments/90456.pdf", 22, "https://www.newsd.admin.ch/newsd/message/attachments/90454.pdf"]

def write(output_file, list_dict, query_num):
    with open(output_file, "a") as f:
            f.write("\n")
            f.write(f"---- Query {query_num} ----")
            for item in list_dict:
                f.write("\n" + str(item))




if __name__ == "__main__":

    database_file = "C:/Users/eroma/Desktop/Master/MA3/DSL_git/DS-Lab/database/production_subset.db"
    output_file = "./exemple_queries.txt"

    try:
        # Connect to the database
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        write(output_file, get_childs_id(cursor, EXEMPLE[0]), 1)
        write(output_file, get_childs_url(cursor, EXEMPLE[0]), 2)
        write(output_file, get_cousin_id(cursor, EXEMPLE[0]), 3)
        write(output_file, get_cousin_url(cursor, EXEMPLE[0]), 4)
        write(output_file, get_parent_id(cursor, EXEMPLE[1]), 5)
        write(output_file, get_parent_url(cursor, EXEMPLE[1]), 6)
        write(output_file, get_pdf_md(cursor, EXEMPLE[2]), 7)
        write(output_file, get_referenced_pdfs_from_page(cursor, EXEMPLE[3]), 8)
        write(output_file, get_stored_file_filename_from_url(cursor, EXEMPLE[4]), 9) 
        
        #write(output_file, get_translated_pdfs(cursor, "pdf"), 10)
        
        #get_simhash_distance()
        #get_similar_pages

        
       



    except sqlite3.Error as e:
        print(f"Error: {e}")
    
