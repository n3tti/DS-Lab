import sqlite3
from multiprocessing import Pool, cpu_count
import re
import json

def count(text):
    if text == None or '':
        return 0
    cleaned_text = re.sub(r'[^a-zA-Z\s]', '', text)
    words = cleaned_text.split()
    return min(round(len(words) / 500) * 500, 20000)

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
    cursor.execute(f"SELECT {field} FROM {table_name} WHERE ((id >= ? AND id <= ?) AND content_formatted_with_markdown IS NOT NULL)", (start_id, end_id))
    print("exec")
    rows = cursor.fetchall()
    wcount = {}

    # Process rows
    for row in rows: 
        text = row[0]
        c = count(text)
        wcount[c] = wcount.get(c, 0) + 1
    conn.close()
    return wcount



def main():
    db_path = "/capstor/store/cscs/swissai/a06/users/group_06/production/data/production_copy_to_parse2.db"
    table_name = "scraped_pages"
    field = "content_formatted_with_markdown"
    num_processes = 80

    print("getting min and max")
    min_id, max_id = get_min_max_id(db_path, table_name)
    range_size = (max_id - min_id + 1) // num_processes
    print("found min max")
    ranges = [(min_id + i * range_size, min_id + (i + 1) * range_size - 1) for i in range(num_processes)]
    ranges[-1] = (ranges[-1][0], max_id) 

    wcount = {}
    results = []
    with Pool(processes=num_processes) as pool:
        results = pool.starmap(process_range, [(db_path, table_name, field, start, end) for start, end in ranges])
    for res in results:
        for key, val in res.items():
            wcount[key] = wcount.get(key, 0) + val
    with open(f"./wcount_{table_name}.txt", "w") as f:
        f.write(json.dumps(wcount))
    

if __name__ == "__main__":
    main()
