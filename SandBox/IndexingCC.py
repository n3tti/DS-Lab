from comcrawl import IndexClient
import requests

# STEP 1 - Get all urls

client = IndexClient(["2024-38"])
crawled_site = "puc.paris/*"
# /!\ common crawl only gets the pages that are allowed in the robot.txt
client.search(crawled_site)
print(len(client.results))
temp = [res for res in client.results if res["status"] == "200"]
for i in temp[0:4]:
  print(i.get("url"))


# STEP 2 - See what we have

print(temp[0])
# urlkey : unique identifier generated from the URL of the crawled page
# timestamp : when it was crawled
# url : url
# mime : content type
# mime-detected: content type detected by the crawler
# status : https status code, 200 = okay
# digest : hash of the page, to check for duplicate content
# length : length
# offset : position of the page content within a larger file, typically a WARC (Web ARChive) file
# filename : name and path of the WARC file where this URL’s data is stored - wget https://data.commoncrawl.org/<filename> " to download the page
# language : detected language
# encoding : encoding


# STEP 3 - Get infos on the dataset

# status
status = set()
for res in client.results:
  status.add(res["status"])
print(status)

#types
client.results = [res for res in client.results if res["status"] == "200"]
types = set()
types_detected = set()
for res in client.results:
  types.add(res["mime"])
  types_detected.add(res["mime-detected"])
print(types)
print(types_detected)

# languages
lang = set()
for res in client.results:
  if res["mime"] == "text/html":
    lang.add(res["languages"])
print(lang)

# duplicates ?
digest = set()
dup = 0
for res in client.results:
  if res["digest"] in digest:
    dup += 1
  digest.add(res["digest"])
print("{} duplicate(s)".format(dup))

# number of pages
files = set()
for res in client.results:
  files.add(res["filename"])
print("{} filess for {} pages.".format(len(files), len(client.results) - dup))

# STEP 4 - Try to get the Common Crawl WARC file on AMAZON S3 (we do not download it now, only the HEAD) and get statistics

# get average size of a file
failed = 0
succes = 0
size = 0
for res in client.results[0:30]:
  filename = res["filename"]
  warc_url = "https://data.commoncrawl.org/{}".format(filename)
  response = requests.head(warc_url)
  if response.status_code == 200:
      file_size_bytes = response.headers.get('Content-Length')
      if file_size_bytes:
        file_size_mb = int(file_size_bytes) / (1024 * 1024)  # Convert to MB
        size += file_size_mb
        succes += 1
      else:
        failed += 1
  else:
    failed += 1
print("Average size : {} MB, {} succes and {} failed.".format(size/succes, succes, failed))

# get HEAD infos
filename = client.results[0]["filename"]
warc_url = "https://data.commoncrawl.org/{}".format(filename)
response = requests.head(warc_url)
if response.status_code == 200:
    file_size_bytes = response.headers.get('Content-Length')
    print(response.headers)
else:
  print("Failed")