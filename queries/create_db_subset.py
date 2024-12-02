"""
Create a subset of a database (from source to target), with a row limit for each table.
Usefull for debuging queries and testing.
 
"""


import sqlite3

def extract_subset(source_db, target_db, row_limit=1000):
    try:
        source_conn = sqlite3.connect(source_db)
        target_conn = sqlite3.connect(target_db)
        source_cursor = source_conn.cursor()
        target_cursor = target_conn.cursor()
        
        # Fetch all table names from the source database
        source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = source_cursor.fetchall()
        
        for table_name in tables:
            table_name = table_name[0]
            print(f"Processing table: {table_name}")
            
            # Fetch the schema of the table
            source_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            create_table_query = source_cursor.fetchone()[0]
            
            # Create the table in the target database
            target_cursor.execute(create_table_query)
            
            # Fetch the first `row_limit` rows from the source table
            source_cursor.execute(f"SELECT * FROM {table_name} LIMIT {row_limit}")
            rows = source_cursor.fetchall()
            
            # Fetch column names for insertion
            source_cursor.execute(f"PRAGMA table_info({table_name})")
            column_names = [info[1] for info in source_cursor.fetchall()]
            column_names_str = ", ".join(column_names)
            placeholders = ", ".join(["?"] * len(column_names))
            
            # Insert rows into the target table
            insert_query = f"INSERT INTO {table_name} ({column_names_str}) VALUES ({placeholders})"
            target_cursor.executemany(insert_query, rows)
        
        # Commit changes to the target database
        target_conn.commit()
        print(f"Subset extracted to {target_db}")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        if source_conn:
            source_conn.close()
        if target_conn:
            target_conn.close()

source_db = "/capstor/store/cscs/swissai/a06/users/group_06/test/production_copy.db"
target_db = "/capstor/store/cscs/swissai/a06/users/group_06/test/production_subset.db"

extract_subset(source_db, target_db, row_limit=2000)