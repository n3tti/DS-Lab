import sqlite3

def write(output_file, text):
    with open(output_file, "a") as f:
            f.write(text)

def count_rows(cursor, table_name, output_file):

    query = f"SELECT COUNT(*) FROM {table_name}"
    cursor.execute(query)
    row_count = cursor.fetchone()[0]
    write(output_file, f"The table '{table_name}' has {row_count} rows.\n")
        
def field_uniqueness(cursor, table_name, field, output_file):

    query = f"""
        SELECT EXISTS(
            SELECT 1
            FROM {table_name}
            GROUP BY {field}
            HAVING COUNT(*) > 1
        )
        """
    cursor.execute(query)
    has_duplicates = cursor.fetchone()[0]
        
    if has_duplicates:
        write(output_file, f"The field '{field}' in table '{table_name}' has duplicate values.\n")
    else:
        write(output_file, f"All values in the field '{field}' in table '{table_name}' are unique.\n")
    
def list_values(cursor, table_name, field, output_file):

    query = f"SELECT DISTINCT {field} FROM {table_name}"
    cursor.execute(query)
        
    values = cursor.fetchall()
    values = [value[0] for value in values]
    write(output_file, f"All distinct values in the field '{field}': {values}\n")

def values_counts(cursor, table_name, field, output_file):

    query = f"""
        SELECT {field}, COUNT(*)
        FROM {table_name}
        GROUP BY {field}
        """
    cursor.execute(query)
    value_counts = cursor.fetchall()
    write(output_file, f"Counts of each unique value in the field '{field}' in table '{table_name}':\n")
    for value, count in value_counts:
            write(output_file, f"Value: {value}, Count: {count}\n")

def min_max(cursor, table_name, field, output_file):
    query = f"""
        SELECT MIN({field}) AS min_value, MAX({field}) AS max_value
        FROM {table_name}
        """
    cursor.execute(query) 
    min_value, max_value = cursor.fetchone()
    write(output_file, f"Minimum value in '{field}' in table '{table_name}': {min_value}\n")
    write(output_file, f"Maximum value in '{field}'in table '{table_name}': {max_value}\n")

def values_dic_keys(cursor, table_name, field, output_file):
    query = f"""
    SELECT DISTINCT json_each.key
    FROM {table_name}, json_each({table_name}.{field})
    """
    cursor.execute(query)
    keys = [row[0] for row in cursor.fetchall()]
    write(output_file, f"All unique keys in the field '{field}' in table '{table_name}': {keys}\n")
    return keys

def distinct_key_sets_count(cursor, table_name, field, output_file):
    
    query = f"""
    SELECT json_group_array(json_each.key) AS key_set, COUNT(*) AS count
    FROM (
        SELECT json_each.key
        FROM {table_name}, json_each({table_name}.{field})
        GROUP BY json_each.key
    ) key_groups
    GROUP BY key_set
    """
    cursor.execute(query)
    results = cursor.fetchall()
    
    write(output_file, f"Distinct sets of keys and their counts in table '{table_name}':\n")
    for row in results:
        key_set, count = row
        write(output_file, f"Keys: {key_set}, Count: {count}\n")
    return results

if __name__ == "__main__":

    database_file = "../database/example.db"
    table_name = "your_table_name"
    output_file = "./stats.txt"

    try:
            # Connect to the database
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        write(output_file, "-----------------   Data summary   -----------------\n")

        #count_rows(cursor, "pdf_links", output_file)
        #count_rows(cursor, "scraped_pages", output_file)
        #count_rows(cursor, "image_links", output_file)
        #count_rows(cursor, "child_parent_links", output_file)

        # field_uniqueness(cursor, "scraped_pages", "url", output_file)
        # field_uniqueness(cursor, "pdf_links", "url", output_file)
        # field_uniqueness(cursor, "image_links", "url", output_file)

        # list_values(cursor, "scraped_pages", "response_status_code", output_file)
        # list_values(cursor, "scraped_pages", "response_content_type", output_file)
        # list_values(cursor, "scraped_pages", "response_content_encoding", output_file)
        # list_values(cursor, "scraped_pages", "response_metadata_lang", output_file)
        # list_values(cursor, "pdf_links", "lang", output_file)

        # values_counts(cursor, "scraped_pages", "status", output_file)
        # values_counts(cursor, "pdf_links", "status", output_file)
        # values_counts(cursor, "image_links", "status", output_file)

        # values_counts(cursor, "scraped_pages", "response_metadata_lang", output_file)

        # min_max(cursor, "scraped_pages", "depth", output_file)
        # min_max(cursor, "scraped_pages", "response_content_length", output_file)

        values_dic_keys(cursor, "scraped_pages", "cousin_urls_dict", output_file)
        
        #distinct_key_sets_count(cursor, "scraped_pages", "cousin_urls_dict", output_file)



    except sqlite3.Error as e:
        print(f"Error: {e}")
    