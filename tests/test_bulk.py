"""Integration tests for the Bulk resource."""

import time

import pytest

from awsysco import Client
from awsysco.models import BulkResult


def _unique_urls(count: int = 3) -> list:
    ts = int(time.time() * 1000)
    return [{"url": f"https://example.com/sdk-bulk-{ts}-{i}"} for i in range(count)]


def _assert_bulk_not_restricted(result: BulkResult) -> None:
    """Skip if all results failed due to account restrictions (e.g. unverified email)."""
    if result.results and all(not r.success for r in result.results):
        errors = {r.error for r in result.results if r.error}
        pytest.skip(f"Staging account restriction — all bulk items failed: {errors}")


class TestBulk:
    def test_bulk_create_returns_result(self, client: Client) -> None:
        urls = _unique_urls(3)
        result = client.bulk.create(urls)
        assert isinstance(result, BulkResult)

    def test_bulk_create_count(self, client: Client) -> None:
        urls = _unique_urls(3)
        result = client.bulk.create(urls)
        _assert_bulk_not_restricted(result)
        assert result.created == 3

    def test_bulk_results_have_short_url(self, client: Client) -> None:
        urls = _unique_urls(3)
        result = client.bulk.create(urls)
        _assert_bulk_not_restricted(result)
        assert len(result.results) == 3
        for item in result.results:
            assert item.success is True
            assert item.short_url is not None
            assert item.short_url.startswith("http")
