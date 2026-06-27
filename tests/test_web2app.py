"""Unit tests for the Web2App resource (sync + async)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

from awsysco.async_resources.web2app import AsyncWeb2AppResource
from awsysco.models import Web2AppSession
from awsysco.resources.web2app import Web2AppResource

_TOKEN = "0123456789abcdef0123456789abcdef"


def _sample_payload():
    return {
        "success": True,
        "linkId": "abc123",
        "utmParams": {"source": "newsletter", "medium": "email"},
        "routingRule": {"country": "US", "redirectUrl": "https://apps.apple.com/app"},
        "country": "US",
        "clickedAt": "2026-01-01T00:00:00Z",
    }


def _make_resource():
    http = MagicMock()
    http.get.return_value = _sample_payload()
    return Web2AppResource(http)


class TestWeb2AppSync:
    def test_consume_calls_correct_endpoint(self):
        resource = _make_resource()
        resource.consume_session(_TOKEN)
        resource._http.get.assert_called_once_with(f"/api/v1/web2app/{_TOKEN}")

    def test_consume_returns_session(self):
        result = _make_resource().consume_session(_TOKEN)
        assert isinstance(result, Web2AppSession)

    def test_consume_populates_fields(self):
        result = _make_resource().consume_session(_TOKEN)
        assert result.success is True
        assert result.link_id == "abc123"
        assert result.country == "US"
        assert result.clicked_at == "2026-01-01T00:00:00Z"

    def test_consume_populates_utm_params(self):
        result = _make_resource().consume_session(_TOKEN)
        assert result.utm_params == {"source": "newsletter", "medium": "email"}

    def test_consume_populates_routing_rule(self):
        result = _make_resource().consume_session(_TOKEN)
        assert result.routing_rule["country"] == "US"

    def test_consume_encodes_token(self):
        resource = _make_resource()
        resource.consume_session("ns/slug")
        resource._http.get.assert_called_once_with("/api/v1/web2app/ns%2Fslug")


def _make_async_resource():
    http = MagicMock()
    http.get = AsyncMock(return_value=_sample_payload())
    return AsyncWeb2AppResource(http)


class TestWeb2AppAsync:
    def test_consume_calls_correct_endpoint(self):
        resource = _make_async_resource()
        asyncio.run(resource.consume_session(_TOKEN))
        resource._http.get.assert_awaited_once_with(f"/api/v1/web2app/{_TOKEN}")

    def test_consume_returns_session(self):
        resource = _make_async_resource()
        result = asyncio.run(resource.consume_session(_TOKEN))
        assert isinstance(result, Web2AppSession)

    def test_consume_populates_fields(self):
        resource = _make_async_resource()
        result = asyncio.run(resource.consume_session(_TOKEN))
        assert result.link_id == "abc123"
        assert result.utm_params == {"source": "newsletter", "medium": "email"}
