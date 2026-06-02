"""Tests for the Analytics resource."""

from __future__ import annotations

import time
from unittest.mock import MagicMock

from awsysco import Client
from awsysco.models import ClickEvent, LinkStats
from awsysco.resources.analytics import AnalyticsResource


# ---------------------------------------------------------------------------
# Unit tests — no network required
# ---------------------------------------------------------------------------

_STATS_DATA = {
    "shortCode": "abc",
    "totalClicks": 42,
    "clicks": [
        {"timestamp": "2026-01-01T00:00:00Z", "country": "US", "device": "desktop"},
    ],
    "aggregateStats": {"byCountry": {"US": 42}},
}


def _make_resource():
    http = MagicMock()
    http.get.return_value = _STATS_DATA
    return AnalyticsResource(http)


class TestAnalyticsUnit:
    def test_get_stats_calls_correct_endpoint(self):
        resource = _make_resource()
        resource.get_stats("abc")
        resource._http.get.assert_called_once_with(
            "/api/v1/links/abc/stats", params=None
        )

    def test_get_stats_with_period(self):
        resource = _make_resource()
        resource.get_stats("abc", period="7d")
        resource._http.get.assert_called_once_with(
            "/api/v1/links/abc/stats", params={"period": "7d"}
        )

    def test_get_stats_returns_link_stats(self):
        resource = _make_resource()
        result = resource.get_stats("abc")
        assert isinstance(result, LinkStats)
        assert result.total_clicks == 42

    def test_get_stats_populates_aggregate_stats(self):
        resource = _make_resource()
        result = resource.get_stats("abc")
        assert result.aggregate_stats is not None
        assert "byCountry" in result.aggregate_stats

    def test_get_recent_clicks_calls_endpoint(self):
        resource = _make_resource()
        resource._http.get.return_value = []
        resource.get_recent_clicks()
        resource._http.get.assert_called_once_with(
            "/api/user/recent-clicks", params=None
        )

    def test_get_recent_clicks_with_limit(self):
        resource = _make_resource()
        resource._http.get.return_value = []
        resource.get_recent_clicks(limit=10)
        resource._http.get.assert_called_once_with(
            "/api/user/recent-clicks", params={"limit": 10}
        )

    def test_get_recent_clicks_returns_list(self):
        resource = _make_resource()
        resource._http.get.return_value = [
            {"timestamp": "2026-01-01T00:00:00Z", "country": "US"}
        ]
        result = resource.get_recent_clicks()
        assert isinstance(result, list)
        assert all(isinstance(c, ClickEvent) for c in result)

    def test_get_recent_clicks_handles_wrapped_response(self):
        resource = _make_resource()
        resource._http.get.return_value = {
            "clicks": [{"timestamp": "2026-01-01T00:00:00Z"}]
        }
        result = resource.get_recent_clicks()
        assert len(result) == 1
        assert isinstance(result[0], ClickEvent)


# ---------------------------------------------------------------------------
# Integration tests — require AWSYS_API_KEY
# ---------------------------------------------------------------------------


def _unique_url() -> str:
    return f"https://example.com/sdk-analytics-{int(time.time() * 1000)}"


class TestAnalytics:
    def test_get_stats_returns_link_stats(self, client: Client) -> None:
        created = client.links.create(_unique_url())
        short_code = created.short_code
        assert short_code is not None

        stats = client.analytics.get_stats(short_code)
        assert isinstance(stats, LinkStats)
        assert stats.total_clicks is not None
        assert isinstance(stats.total_clicks, int)

    def test_get_stats_has_clicks_list(self, client: Client) -> None:
        created = client.links.create(_unique_url())
        short_code = created.short_code
        assert short_code is not None

        stats = client.analytics.get_stats(short_code)
        assert isinstance(stats.clicks, list)
