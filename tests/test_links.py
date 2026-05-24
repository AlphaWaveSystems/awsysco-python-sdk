"""Integration tests for the Links resource."""

import time

import pytest

from awsysco import Client, AwsysNotFoundError
from awsysco.models import Link, LinkList


def _unique_url() -> str:
    return f"https://example.com/sdk-test-{int(time.time() * 1000)}"


class TestLinksCreate:
    def test_create_returns_link(self, client: Client) -> None:
        link = client.links.create(_unique_url())
        assert isinstance(link, Link)
        assert link.short_url is not None
        assert link.short_url.startswith("http")

    def test_create_with_max_clicks(self, client: Client) -> None:
        link = client.links.create(_unique_url(), max_clicks=999)
        assert isinstance(link, Link)
        assert link.short_url is not None


class TestLinksList:
    def test_list_returns_link_list(self, client: Client) -> None:
        result = client.links.list(limit=5)
        assert isinstance(result, LinkList)
        assert isinstance(result.links, list)

    def test_list_default_limit(self, client: Client) -> None:
        result = client.links.list()
        assert result.links is not None


class TestLinksGet:
    def test_get_returns_correct_link(self, client: Client) -> None:
        # Create a link first
        created = client.links.create(_unique_url())
        short_code = created.short_code
        assert short_code is not None

        fetched = client.links.get(short_code)
        assert isinstance(fetched, Link)
        assert fetched.short_code == short_code


class TestLinksUpdate:
    def test_update_max_clicks(self, client: Client) -> None:
        created = client.links.create(_unique_url())
        short_code = created.short_code
        assert short_code is not None

        updated = client.links.update(short_code, max_clicks=100)
        assert isinstance(updated, Link)
        assert updated.max_clicks == 100


class TestLinksDelete:
    def test_delete_then_get_raises_not_found(self, client: Client) -> None:
        created = client.links.create(_unique_url())
        short_code = created.short_code
        assert short_code is not None

        client.links.delete(short_code)

        with pytest.raises(AwsysNotFoundError):
            client.links.get(short_code)
