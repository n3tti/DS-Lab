import json

import pytest

from adminch_crawler.config import PARENTS_DIR, METADATA_DIR

@pytest.fixture(scope="session")
def load_metadata():
    with open(METADATA_DIR, "r") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def load_parents():
    with open(PARENTS_DIR, "r") as f:
        return json.load(f)