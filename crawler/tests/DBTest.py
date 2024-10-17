import json

import pytest

metadata_file = "./metadata.json"
parents_file = "./parents.json"


@pytest.fixture
def load_metadata():
    with open(metadata_file, "r") as f:
        return json.load(f)


@pytest.fixture
def load_parents():
    with open(parents_file, "r") as f:
        return json.load(f)


# Unique IDs
def test_unique_ids(load_metadata):
    data = load_metadata
    ids = [item["id"] for item in data if "id" in item]
    assert len(ids) == len(set(ids)), "IDs are not unique."


# No duplicate parents
def test_unique_parents(load_parents):
    data = load_parents
    for item in data:
        assert len(item["parents"]) == len(set(item["parents"])), "Parents are not unique."


# Every item has a url
def test_has_url(load_metadata):
    data = load_metadata
    for item in data:
        assert "url" in item, "No url."
        assert item["url"] != "", "Empty url."


# No duplicate urls
def test_unique_urls(load_metadata):
    data = load_metadata
    urls = [item["url"] for item in data if "url" in item]
    assert len(urls) == len(set(urls)), "Urls are not unique."


# Each language appears at most once
def test_unique_languages(load_metadata):
    data = load_metadata
    for item in data:
        assert len(item["cousin_urls"].keys()) == len(
            set(item["cousin_urls"].keys())
        ), "A language appears more than once."


# Each cousin ID is referenced in Metadata and the lanuguage is known
def test_cousin_url_is_referenced_and_language_is_known(load_metadata):
    data = load_metadata
    ids = [item["id"] for item in data]
    langs = ["de", "fr", "it", "rm", "en"]
    for item in data:
        for lang, id in item["cousin_urls"].items():
            assert lang in langs, "Other language found."
            assert id in ids, "A cousin url is not referenced."


# Each child and parent ID is referenced in Metadata
def test_each_child_and_parent_is_referenced(load_parents, load_metadata):
    data1 = load_parents
    data2 = load_metadata
    ids = [item["id"] for item in data2]
    for child in data1:
        assert child["id"] in ids, "A child is not referenced."
        for parent in child["parents"]:
            assert parent in ids, "A parent is not referenced."


# Every item has a language
def test_item_has_language(load_metadata):
    data = load_metadata
    langs = ["de", "fr", "it", "rm", "en"]
    for item in data:
        assert "lang" in item, "Item without a language."
        assert item["lang"] in langs, "An item has unknown language."


# Lang attribute and cousin_url lang attribute has to match
def test_lang_consistency(load_metadata):
    data = load_metadata
    lang_by_id = {item["id"]: item["lang"] for item in data}
    for item in data:
        for lang, id in item["cousin_urls"]:
            if id in lang_by_id:
                assert lang_by_id[id] == lang, "Cousin language and item language do not match."


# more test to do:
# check consistency of metadata
# check for duplicate hash
# check for url problem with de->fr
