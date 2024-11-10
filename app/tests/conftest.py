import json
from unittest.mock import Mock, create_autospec, patch

import pytest
from factory.fuzzy import FuzzyText
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture
from scrapy.spiders import Spider

from app.config import METADATA_DIR, PARENTS_DIR
from app.repository.db import Database
from app.repository.models import ScrapedPage


@register_fixture
class ScrapedPageFactory(ModelFactory):
    __model__ = ScrapedPage


@pytest.fixture
def mock_spider():
    return Spider(name="test_spider")
