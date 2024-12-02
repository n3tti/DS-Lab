"""
Run and outputs the results of exemple-queries provided in README.md
 
"""
import sqlite3

def write(output_file, text, query_num):
    with open(output_file, "a") as f:
            f.write(f"---- Query {query_num} ----")
            f.write(text)

def query1(cursor, output_file):
    #  Given a page id, get pages same pages in different languages.

    id_url_query = "SELECT id, url FROM scraped_pages LIMIT 1"
    cursor.execute(id_url_query)
    id, url = cursor.fetchone()[0]

    other_id_query = f"SELECT cousin_url FROM scraped_pages where id == {id} limit 1"
    dic = f"SELECT COUNT(*) FROM {table_name}"
    cursor.execute(query)
    row_count = cursor.fetchone()[0]
    write(output_file, "", 1)
        


if __name__ == "__main__":

    database_file = "/capstor/store/cscs/swissai/a06/users/group_06/test/production_subset.db"
    output_file = "./exemple_queries.txt"

    try:
            # Connect to the database
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        
        query1(cursor, output_file)



    except sqlite3.Error as e:
        print(f"Error: {e}")
    
