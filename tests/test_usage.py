"""Unit tests for the Usage resource (sync + async)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

from awsysco.async_resources.usage import AsyncUsageResource
from awsysco.models import UsageStats
from awsysco.resources.usage import UsageResource


def _sample_payload():
    return {
        "totalLinks": 12,
        "totalClicks": 340,
        "linksCreatedThisMonth": 5,
        "qrCodesThisMonth": 2,
        "folderCount": 3,
        "apiCallsThisMonth": 88,
        "trackedClicksThisMonth": 120,
        "tier": "pro",
        "limits": {
            # Mix of an integer cap and an "unlimited" literal.
            "linksPerMonth": "unlimited",
            "monthlyLinks": "unlimited",
            "dailyLinks": 100,
            "monthlyTrackedClicks": 50000,
            "apiCallsPerMonth": 10000,
            "qrCodes": "unlimited",
            "folders": 50,
            "customSlugs": 25,
        },
        "hasApiKey": True,
        "apiKeyCreatedAt": "2026-01-01T00:00:00Z",
        "userPrefix": "demo",
        "isPremium": True,
        "overage": {
            "active": False,
            "startedAt": None,
            "expiresAt": None,
            "hoursUntilDrop": None,
            "clicksThisCycle": 0,
            "spendingLimitCents": 0,
            "estimatedChargeCents": 0,
        },
    }


def _make_resource():
    http = MagicMock()
    http.get.return_value = _sample_payload()
    return UsageResource(http)


class TestUsageSync:
    def test_get_calls_correct_endpoint(self):
        resource = _make_resource()
        resource.get()
        resource._http.get.assert_called_once_with("/api/user/stats")

    def test_get_returns_usage_stats(self):
        result = _make_resource().get()
        assert isinstance(result, UsageStats)

    def test_get_populates_counters(self):
        result = _make_resource().get()
        assert result.total_links == 12
        assert result.total_clicks == 340
        assert result.api_calls_this_month == 88
        assert result.tracked_clicks_this_month == 120
        assert result.tier == "pro"

    def test_unlimited_limit_value(self):
        result = _make_resource().get()
        assert result.limits.links_per_month == "unlimited"
        assert result.limits.qr_codes == "unlimited"

    def test_integer_limit_value(self):
        result = _make_resource().get()
        assert result.limits.daily_links == 100
        assert result.limits.custom_slugs == 25

    def test_overage_nested_model(self):
        result = _make_resource().get()
        assert result.overage.active is False
        assert result.overage.estimated_charge_cents == 0

    def test_has_api_key_and_prefix(self):
        result = _make_resource().get()
        assert result.has_api_key is True
        assert result.user_prefix == "demo"
        assert result.is_premium is True


def _make_async_resource():
    http = MagicMock()
    http.get = AsyncMock(return_value=_sample_payload())
    return AsyncUsageResource(http)


class TestUsageAsync:
    def test_get_calls_correct_endpoint(self):
        resource = _make_async_resource()
        asyncio.run(resource.get())
        resource._http.get.assert_awaited_once_with("/api/user/stats")

    def test_get_returns_usage_stats(self):
        resource = _make_async_resource()
        result = asyncio.run(resource.get())
        assert isinstance(result, UsageStats)

    def test_unlimited_limit_value(self):
        resource = _make_async_resource()
        result = asyncio.run(resource.get())
        assert result.limits.monthly_links == "unlimited"
        assert result.limits.folders == 50
