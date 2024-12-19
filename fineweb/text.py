import duckdb

# Query directly from Parquet file
con = duckdb.connect()
file = "/capstor/store/cscs/swissai/a06/datasets_raw/fineweb-edu-full/data/CC-MAIN-2013-20/train-00000-of-00014.parquet"
query = f"SELECT url, text FROM '{file}' LIMIT 1000"
result = con.execute(query).fetchdf()
print(result)
with open("res.txt", "w") as f:
    f.write(result.to_string())
