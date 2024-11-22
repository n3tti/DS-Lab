import json
import random
import time
from collections import defaultdict

import requests


def get_archive_names():
    index_response = requests.get("https://index.commoncrawl.org/collinfo.json")
    if index_response.status_code == 200:
        index_data = index_response.json()
        return [index["id"] for index in sorted(index_data, key=lambda x: x["id"], reverse=True)[:2]]
    else:
        print("Failed to fetch archive names")
    return []


def fetch_all_index_data(domain, index_name):
    api_url = f"http://index.commoncrawl.org/{index_name}-index"
    all_records = []
    page = 0
    while True:
        # for i in range(1):
        params = {
            "url": f"*.{domain}/*",
            "output": "json",
            # 'pageSize': 100,
            "page": page,
        }

        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            new_records = [json.loads(line) for line in response.iter_lines() if line]
            if not new_records:
                break
            all_records.extend(new_records)
            num_entries = len(new_records)
            print(f"Page {page}: Retrieved {num_entries} records")
            page += 1
        else:
            print(f"Failed to fetch data from {index_name}, HTTP status: {response.status_code}")
            break

        time.sleep(5)

    print(f"Found {len(all_records)} records in archive {index_name}")
    return all_records


archives = get_archive_names()
domain = "admin.ch"

all_records = []
for archive in archives:
    records = fetch_all_index_data(domain, archive)
    all_records.extend(records)

print(f"Total records found: {len(all_records)}")

# sample_records = random.sample(all_records, min(len(all_records), 20)) if all_records else []
status_200_records = [x for x in all_records if x.get("status") == "200"]
print(f"Total status=200 records found: {len(status_200_records)}")


unique_records = {r["url"]: r for r in status_200_records}.values()
print(f"Unique records by url with status=200: {len(unique_records)}")


url_count = defaultdict(int)
for record in status_200_records:
    url_count[record["url"]] += 1
duplicates = [rec for rec in status_200_records if url_count[rec["url"]] > 1]
print(f"Number of duplicate records: {len(duplicates)}")
# for rec in duplicates:
#     print(rec['url'])
