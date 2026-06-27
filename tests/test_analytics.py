"""Tests for the Analytics resource."""

from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

from awsysco import Client
from awsysco.async_resources.analytics import AsyncAnalyticsResource
from awsysco.models import AggregateAnalytics, ClickEvent, LinkStats
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
# Aggregate stats — mocked, tier-gated (free + pro)
# ---------------------------------------------------------------------------

_FREE_AGGREGATE = {
    "shortCode": "abc",
    "fullPath": "abc",
    "period": "30d",
    "totalClicks": 120,
    "uniqueVisitors": 80,
    "clicksByDay": [
        {"date": "2026-01-01", "clicks": 60},
        {"date": "2026-01-02", "clicks": 60},
    ],
    "countryBreakdown": {"US": 100, "CA": 20},
    "tierLimit": 30,
    "tier": "free",
    "upgradeForMore": {
        "available": ["deviceBreakdown", "utmBreakdown", "hourBreakdown"],
        "message": "Upgrade to Pro for device, UTM, and hourly breakdowns.",
    },
}

_PRO_AGGREGATE = {
    "shortCode": "abc",
    "fullPath": "acme/abc",
    "period": "30d",
    "totalClicks": 5000,
    "uniqueVisitors": 3200,
    "clicksByDay": [{"date": "2026-01-01", "clicks": 5000}],
    "countryBreakdown": {"US": 4000, "GB": 1000},
    "tierLimit": 365,
    "tier": "pro",
    "deviceBreakdown": {"mobile": 3000, "desktop": 1800, "tablet": 200},
    "referrerBreakdown": {"twitter.com": 1200},
    "browserBreakdown": {"Chrome": 3500},
    "osBreakdown": {"iOS": 2800},
    "sourceBreakdown": {"newsletter": 900},
    "hourBreakdown": [{"hour": 9, "clicks": 400}, {"hour": 10, "clicks": 600}],
    "utmBreakdown": {
        "sources": {"newsletter": 900},
        "mediums": {"email": 900},
        "campaigns": {"launch": 700},
    },
}


def _make_aggregate_resource(payload):
    http = MagicMock()
    http.get.return_value = payload
    return AnalyticsResource(http)


class TestAggregateAnalyticsSync:
    def test_calls_aggregate_endpoint(self):
        resource = _make_aggregate_resource(_FREE_AGGREGATE)
        resource.get_aggregate_stats("abc")
        resource._http.get.assert_called_once_with(
            "/api/v1/links/abc/stats/aggregate", params=None
        )

    def test_passes_period_param(self):
        resource = _make_aggregate_resource(_FREE_AGGREGATE)
        resource.get_aggregate_stats("abc", period="30d")
        resource._http.get.assert_called_once_with(
            "/api/v1/links/abc/stats/aggregate", params={"period": "30d"}
        )

    def test_free_tier_upgrade_for_more(self):
        result = _make_aggregate_resource(_FREE_AGGREGATE).get_aggregate_stats("abc")
        assert isinstance(result, AggregateAnalytics)
        assert result.tier == "free"
        assert result.total_clicks == 120
        assert result.unique_visitors == 80
        assert result.country_breakdown == {"US": 100, "CA": 20}
        assert len(result.clicks_by_day) == 2
        assert result.clicks_by_day[0].date == "2026-01-01"
        # free tier omits the richer breakdowns
        assert result.device_breakdown is None
        assert result.utm_breakdown is None
        # but surfaces the upgrade hint
        assert result.upgrade_for_more is not None
        assert "deviceBreakdown" in result.upgrade_for_more.available

    def test_pro_tier_device_breakdown(self):
        result = _make_aggregate_resource(_PRO_AGGREGATE).get_aggregate_stats("abc")
        assert result.tier == "pro"
        assert result.full_path == "acme/abc"
        assert result.device_breakdown is not None
        assert result.device_breakdown.mobile == 3000
        assert result.device_breakdown.tablet == 200
        assert result.utm_breakdown.sources == {"newsletter": 900}
        assert result.hour_breakdown[1].hour == 10
        assert result.upgrade_for_more is None


def _make_async_aggregate_resource(payload):
    http = MagicMock()
    http.get = AsyncMock(return_value=payload)
    return AsyncAnalyticsResource(http)


class TestAggregateAnalyticsAsync:
    def test_calls_aggregate_endpoint(self):
        resource = _make_async_aggregate_resource(_FREE_AGGREGATE)
        asyncio.run(resource.get_aggregate_stats("abc", period="7d"))
        resource._http.get.assert_awaited_once_with(
            "/api/v1/links/abc/stats/aggregate", params={"period": "7d"}
        )

    def test_free_tier_upgrade_for_more(self):
        resource = _make_async_aggregate_resource(_FREE_AGGREGATE)
        result = asyncio.run(resource.get_aggregate_stats("abc"))
        assert isinstance(result, AggregateAnalytics)
        assert result.tier == "free"
        assert result.device_breakdown is None
        assert result.upgrade_for_more.message.startswith("Upgrade to Pro")

    def test_pro_tier_device_breakdown(self):
        resource = _make_async_aggregate_resource(_PRO_AGGREGATE)
        result = asyncio.run(resource.get_aggregate_stats("abc"))
        assert result.device_breakdown.desktop == 1800
        assert result.utm_breakdown.campaigns == {"launch": 700}


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
