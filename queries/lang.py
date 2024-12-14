import sqlite3
from multiprocessing import Pool, cpu_count
import re
import json

def normalize(lang):
    if lang == None or '':
        return "Unknown"
    clean_lang = re.sub(r'[^a-zA-Z]', '', lang.strip()).lower()
    if "en" in clean_lang:
        return "EN"
    if "de" in clean_lang:
        return "DE"
    if "fr" in clean_lang:
        return "FR"
    if "it" in clean_lang:
        return "IT"
    if "rm" in clean_lang:
        return "RM"
    if clean_lang == "":
        return "Unknown"
    return "Other"

def get_min_max_id(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT MIN(id), MAX(id) FROM {table_name}")
    min_id, max_id = cursor.fetchone()
    conn.close()
    return min_id, max_id

def process_range(db_path, table_name, field, start_id, end_id):
    """Worker function to process a specific range of rows."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query the range
    cursor.execute(f"SELECT {field} FROM {table_name} WHERE id >= ? AND id <= ?", (start_id, end_id))
    rows = cursor.fetchall()
    lang_dic = {"EN" : 0, "DE": 0, "FR":0, "IT" : 0, "RM": 0, "Other": 0, "Unknown" : 0}

    # Process rows
    for row in rows: 
        lang = row[0]
        n_lang = normalize(lang)
        lang_dic[n_lang] += 1
    conn.close()
    return lang_dic



def main():
    db_path = "/capstor/store/cscs/swissai/a06/users/group_06/production/data/production_copy_to_stats.db"
    table_name = "scraped_pages"
    field = "response_metadata_lang"
    outputfile = "./lang.txt"

    num_processes = 2

    # Get the range of IDs
    min_id, max_id = get_min_max_id(db_path, table_name)
    range_size = (max_id - min_id + 1) // num_processes

    # Create ranges for each process
    ranges = [(min_id + i * range_size, min_id + (i + 1) * range_size - 1) for i in range(num_processes)]
    ranges[-1] = (ranges[-1][0], max_id)  # Adjust the last range to include the remainder

    # Use multiprocessing to process ranges
    lang_dic = {"EN" : 0, "DE": 0, "FR":0, "IT" : 0, "RM": 0, "Other": 0, "Unknown" : 0}
    results = []
    with Pool(processes=num_processes) as pool:
        results = pool.starmap(process_range, [(db_path, table_name, field, start, end) for start, end in ranges])
    for res in results:
        for key, val in res.items():
            lang_dic[key] += val
    with open(outputfile, "a") as f:
        f.write(f"Lang for table {table_name}: " + json.dumps(lang_dic))

    

if __name__ == "__main__":
    main()
