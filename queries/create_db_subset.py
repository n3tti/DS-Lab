"""
Create a subset of a database (from source to target), with a row limit for each table.
Usefull for debuging queries and testing.
 
"""
import sqlite3

SOURCE_DB = "/capstor/store/cscs/swissai/a06/users/group_06/test/production_copy.db"
TARGET_DB = "/capstor/store/cscs/swissai/a06/users/group_06/test/production_subset.db"
ROW_LIMIT = 2000

def extract_subset(source_db, target_db, row_limit=1000):
    try:
        source_conn = sqlite3.connect(source_db)
        target_conn = sqlite3.connect(target_db)
        source_cursor = source_conn.cursor()
        target_cursor = target_conn.cursor()   
        source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = source_cursor.fetchall()
        
        for table_name in tables:
            table_name = table_name[0]
            print(f"Processing table: {table_name}")
            source_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            create_table_query = source_cursor.fetchone()[0]
            target_cursor.execute(create_table_query)
            source_cursor.execute(f"SELECT * FROM {table_name} LIMIT {row_limit}")
            rows = source_cursor.fetchall()
            
            source_cursor.execute(f"PRAGMA table_info({table_name})")
            column_names = [info[1] for info in source_cursor.fetchall()]
            column_names_str = ", ".join(column_names)
            placeholders = ", ".join(["?"] * len(column_names))
            
            insert_query = f"INSERT INTO {table_name} ({column_names_str}) VALUES ({placeholders})"
            target_cursor.executemany(insert_query, rows)
        
        target_conn.commit()
        print(f"Subset extracted to {target_db}")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        if source_conn:
            source_conn.close()
        if target_conn:
            target_conn.close()

if __name__ == "__main__":
    extract_subset(SOURCE_DB, TARGET_DB, row_limit=ROW_LIMIT)