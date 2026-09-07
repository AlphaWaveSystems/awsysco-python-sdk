"""Tests for the Links resource."""

from __future__ import annotations

import time
from unittest.mock import MagicMock

import pytest

from awsysco import Client, AwsysNotFoundError
from awsysco.models import GeoRestriction, Link, LinkList, OgMeta, RoutingRule
from awsysco.resources.links import LinksResource


# ---------------------------------------------------------------------------
# Unit tests — no network required
# ---------------------------------------------------------------------------

_LINK_DATA = {
    "id": "link1",
    "shortUrl": "https://awsys.co/abc",
    "shortCode": "abc",
    "long": "https://example.com",
    "clicks": 0,
}


def _make_resource(return_value=None):
    http = MagicMock()
    http.post.return_value = return_value or _LINK_DATA
    http.get.return_value = return_value or _LINK_DATA
    http.patch.return_value = return_value or _LINK_DATA
    http.delete.return_value = None
    return LinksResource(http)


class TestLinksCreateUnit:
    def test_create_sends_url(self):
        resource = _make_resource()
        resource.create("https://example.com")
        body = resource._http.post.call_args[1]["json"]
        assert body["url"] == "https://example.com"

    def test_create_sends_custom_slug(self):
        resource = _make_resource()
        resource.create("https://example.com", custom_slug="myslug")
        body = resource._http.post.call_args[1]["json"]
        assert body["customSlug"] == "myslug"

    def test_create_sends_routing_rules(self):
        resource = _make_resource()
        rules = [{"country": "US", "redirectUrl": "https://us.example.com"}]
        resource.create("https://example.com", routing_rules=rules)
        body = resource._http.post.call_args[1]["json"]
        assert body["routingRules"] == rules

    def test_create_sends_og_meta(self):
        resource = _make_resource()
        og = {"title": "My Title", "description": "desc"}
        resource.create("https://example.com", og_meta=og)
        body = resource._http.post.call_args[1]["json"]
        assert body["ogMeta"] == og

    def test_create_sends_geo_restriction(self):
        resource = _make_resource()
        geo = {"allowedCountries": ["US", "CA"]}
        resource.create("https://example.com", geo_restriction=geo)
        body = resource._http.post.call_args[1]["json"]
        assert body["geoRestriction"] == geo

    def test_create_sends_password(self):
        resource = _make_resource()
        resource.create("https://example.com", password="secret")
        body = resource._http.post.call_args[1]["json"]
        assert body["password"] == "secret"

    def test_create_sends_pass_ad_click_ids(self):
        resource = _make_resource()
        resource.create("https://example.com", pass_ad_click_ids=True)
        body = resource._http.post.call_args[1]["json"]
        assert body["passAdClickIds"] is True

    def test_create_sends_folder_id(self):
        resource = _make_resource()
        resource.create("https://example.com", folder_id="folder1")
        body = resource._http.post.call_args[1]["json"]
        assert body["folderId"] == "folder1"

    def test_create_sends_tags(self):
        resource = _make_resource()
        resource.create("https://example.com", tags=["promo", "social"])
        body = resource._http.post.call_args[1]["json"]
        assert body["tags"] == ["promo", "social"]

    def test_create_returns_link(self):
        resource = _make_resource()
        result = resource.create("https://example.com")
        assert isinstance(result, Link)

    def test_update_sends_url(self):
        resource = _make_resource()
        resource.update("abc", url="https://new.example.com")
        body = resource._http.patch.call_args[1]["json"]
        assert body["url"] == "https://new.example.com"

    def test_update_sends_tags(self):
        resource = _make_resource()
        resource.update("abc", tags=["new-tag"])
        body = resource._http.patch.call_args[1]["json"]
        assert body["tags"] == ["new-tag"]

    def test_update_omits_none_fields(self):
        resource = _make_resource()
        resource.update("abc", max_clicks=50)
        body = resource._http.patch.call_args[1]["json"]
        assert "url" not in body
        assert "tags" not in body
        assert body["maxClicks"] == 50

    def test_update_encodes_namespaced_short_path(self):
        resource = _make_resource()
        resource.update("acme/abc", max_clicks=50)
        path = resource._http.patch.call_args[0][0]
        assert path == "/api/v1/links/acme%2Fabc"

    def test_create_accepts_typed_models(self):
        resource = _make_resource()
        resource.create(
            "https://example.com",
            routing_rules=[RoutingRule(country="US", redirect_url="https://us.example.com")],
            og_meta=OgMeta(title="My Title"),
            geo_restriction=GeoRestriction(allowed_countries=["US"]),
        )
        body = resource._http.post.call_args[1]["json"]
        assert body["routingRules"] == [
            {"country": "US", "redirectUrl": "https://us.example.com"}
        ]
        assert body["ogMeta"] == {"title": "My Title"}
        assert body["geoRestriction"] == {"allowedCountries": ["US"]}

    def test_create_still_accepts_plain_dicts(self):
        resource = _make_resource()
        resource.create(
            "https://example.com",
            og_meta={"title": "Dict Title"},
        )
        body = resource._http.post.call_args[1]["json"]
        assert body["ogMeta"] == {"title": "Dict Title"}


class TestLinksListAll:
    def test_list_all_stops_on_has_more_false(self):
        resource = _make_resource()
        resource._http.get.side_effect = [
            {"links": [_LINK_DATA, _LINK_DATA], "hasMore": True},
            {"links": [_LINK_DATA], "hasMore": False},
        ]
        results = list(resource.list_all(limit=2))
        assert len(results) == 3
        assert resource._http.get.call_count == 2

    def test_list_all_stops_on_short_page_without_has_more(self):
        resource = _make_resource()
        resource._http.get.side_effect = [
            {"links": [_LINK_DATA, _LINK_DATA]},
            {"links": [_LINK_DATA]},
        ]
        results = list(resource.list_all(limit=2))
        assert len(results) == 3
        assert resource._http.get.call_count == 2

    def test_list_all_stops_on_empty_first_page(self):
        resource = _make_resource()
        resource._http.get.return_value = {"links": []}
        results = list(resource.list_all(limit=20))
        assert results == []
        assert resource._http.get.call_count == 1

    def test_list_all_clamps_limit_to_100(self):
        resource = _make_resource()
        resource._http.get.return_value = {"links": []}
        list(resource.list_all(limit=500))
        assert resource._http.get.call_args[1]["params"]["limit"] == 100

    def test_list_all_clamps_zero_and_negative_limit(self):
        """limit=0 (or negative) must clamp to >=1 and terminate — a bare
        min(limit, 100) with no lower bound would send limit=0 to the platform,
        and if a page ever came back non-empty, loop forever (`len(page.links) <
        0` is never true, so the short-page stop condition could never fire)."""
        resource = _make_resource()
        resource._http.get.return_value = {"links": []}
        results = list(resource.list_all(limit=0))
        assert resource._http.get.call_args[1]["params"]["limit"] == 1
        assert results == []
        assert resource._http.get.call_count == 1  # terminates after one page

        resource2 = _make_resource()
        resource2._http.get.return_value = {"links": []}
        list(resource2.list_all(limit=-5))
        assert resource2._http.get.call_args[1]["params"]["limit"] == 1


# ---------------------------------------------------------------------------
# Integration tests — require AWSYS_API_KEY
# ---------------------------------------------------------------------------


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
