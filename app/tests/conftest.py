import json

import pytest
from app.config import METADATA_DIR, PARENTS_DIR
from factory.fuzzy import FuzzyText
from pydantic_factories import Ignore, ModelFactory
from pydantic_factories.plugins.pytest_plugin import register_fixture
from unittest.mock import Mock
from unittest.mock import patch, create_autospec
from app.repository.models import ScrapedPage
from scrapy.spiders import Spider
from app.repository.db import Database


@register_fixture
class ScrapedPageFactory(ModelFactory):
    __model__ = ScrapedPage


@pytest.fixture
def mock_spider():
    return Spider(name='test_spider')

