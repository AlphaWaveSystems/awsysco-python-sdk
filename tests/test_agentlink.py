"""Unit tests for the AgentLink resource."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from awsysco.resources.agentlink import AgentlinkResource


def _make_resource():
    http = MagicMock()
    http.post.return_value = {"subscribed": True}
    http.get.return_value = {"clicks": 42}
    return AgentlinkResource(http)


class TestAgentlink:
    def test_subscribe_calls_correct_endpoint(self):
        resource = _make_resource()
        resource.subscribe("user@example.com")
        resource._http.post.assert_called_once_with(
            "/api/agentlink/subscribe", json={"email": "user@example.com"}
        )

    def test_subscribe_returns_dict(self):
        resource = _make_resource()
        result = resource.subscribe("user@example.com")
        assert isinstance(result, dict)

    def test_get_link_stats_calls_correct_endpoint(self):
        resource = _make_resource()
        resource.get_link_stats("abc123")
        resource._http.get.assert_called_once_with(
            "/api/agentlink/links/abc123/stats", params={"period": 7}
        )

    def test_get_link_stats_custom_period(self):
        resource = _make_resource()
        resource.get_link_stats("abc123", period_days=30)
        resource._http.get.assert_called_once_with(
            "/api/agentlink/links/abc123/stats", params={"period": 30}
        )

    def test_get_account_stats_calls_correct_endpoint(self):
        resource = _make_resource()
        resource.get_account_stats()
        resource._http.get.assert_called_once_with(
            "/api/agentlink/account/stats", params={"period": 7}
        )

    def test_get_account_stats_custom_period(self):
        resource = _make_resource()
        resource.get_account_stats(period_days=14)
        resource._http.get.assert_called_once_with(
            "/api/agentlink/account/stats", params={"period": 14}
        )
