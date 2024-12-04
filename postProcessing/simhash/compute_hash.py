from app.repository.db import db
from simhash import Simhash
import re


ROW_PER_READ = 50
NGRAMS = 3
# Hash == '1' stands for null content or empty content. Hash == '0' stands for processing hash.

def get_features(s):
    width = NGRAMS
    s = s.lower()
    s = re.sub(r"[^\w]+", "", s)
    return [s[i : i + width] for i in range(max(len(s) - width + 1, 1))]


def get_hash(text):
    return str(Simhash(get_features(text)).value)

def compute_simhash():
    rows = db.get_none_hash(ROW_PER_READ)
    for row in rows:
        hash = '1'
        #text = row.content_formatted_with_markdown # get the simash over the processed html!!!!!
        print("Please, modify text and make sure the db is updated with 'content_formatted_with_markdown' field.")
        return
        text = row.response_text
        if not (text == None or len(text) == 0):
            hash = get_hash(text)
        db.update_hash(row.id, hash)
        print(f"Updated hash : {hash}")


def compute():
    while True:
        compute_simhash()


if __name__ == "__main__":
    compute()