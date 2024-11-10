from unittest.mock import Mock, patch

import pytest
from scrapy.exceptions import DropItem
from scrapy.spiders import Spider

from app.adminch_crawler.pipelines import FilterURLPipeline
from app.repository.models import ScrapedPage, StatusEnum
from app.tests.conftest import ScrapedPageFactory

from pydantic import ValidationError


# @pytest.mark.skip
@patch("app.adminch_crawler.pipelines.db")
def test_scraped_page_pipeline_response_status_code_ne_200(mock_db, mock_spider: Spider, scraped_page_factory: ScrapedPageFactory):
    scraped_page = scraped_page_factory.build(response_status_code=404)
    mock_db.update_scraped_page_status = Mock()

    pipeline = FilterURLPipeline()

    with pytest.raises(DropItem) as exc_info:
        pipeline.process_item(scraped_page, mock_spider)

    mock_db.update_scraped_page_status.assert_called_with(scraped_page.id, StatusEnum.FAILED)
    assert str(exc_info.value) == f"HTTP Status: {scraped_page.response_status_code}: {scraped_page}."


@patch("app.adminch_crawler.pipelines.db")
def test_scraped_page_pipeline_response_content_type_is_none(mock_db, mock_spider: Spider, scraped_page_factory: ScrapedPageFactory):
    scraped_page = scraped_page_factory.build(response_status_code=200, response_content_type=b"1234text/html;charset=utf-8")
    mock_db.update_scraped_page_status = Mock()

    pipeline = FilterURLPipeline()

    with pytest.raises(DropItem) as exc_info:
        pipeline.process_item(scraped_page, mock_spider)

    mock_db.update_scraped_page_status.assert_called_with(scraped_page.id, StatusEnum.FAILED)
    assert str(exc_info.value) == f"Content type \"{scraped_page.response_content_type.split(';')[0]}\" is not allowed."


def test_decode_utf8_validator():
    # valid input test
    input_value = b"text/html; charset=utf-8"
    page = ScrapedPage(response_content_type=input_value)
    assert page.response_content_type == "text/html; charset=utf-8"

    input_value = None
    page = ScrapedPage(response_content_type=input_value)
    assert page.response_content_type is None

    # non-bytes pass through unchanged
    input_value = "text/html"
    page = ScrapedPage(response_content_type=input_value)
    assert page.response_content_type == "text/html"

    with pytest.raises(ValidationError):
        page = ScrapedPage(response_content_type=123)
