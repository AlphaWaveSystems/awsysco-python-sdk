"""Unit tests for the Webhooks resource."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from awsysco.models import Webhook
from awsysco.resources.webhooks import WebhooksResource


_WEBHOOK_DATA = {
    "id": "wh1",
    "url": "https://example.com/hook",
    "events": ["link.created", "link.click"],
    "name": "My Webhook",
    "enabled": True,
    "createdAt": "2026-01-01T00:00:00Z",
}


def _make_resource():
    http = MagicMock()
    http.get.return_value = {"webhooks": [_WEBHOOK_DATA]}
    http.post.return_value = _WEBHOOK_DATA
    http.patch.return_value = _WEBHOOK_DATA
    http.delete.return_value = None
    return WebhooksResource(http)


class TestWebhooks:
    def test_list_event_types_calls_endpoint(self):
        resource = _make_resource()
        resource._http.get.return_value = {"eventTypes": ["link.created"]}
        resource.list_event_types()
        resource._http.get.assert_called_once_with("/api/webhooks/event-types")

    def test_list_calls_endpoint(self):
        resource = _make_resource()
        resource.list()
        resource._http.get.assert_called_once_with("/api/webhooks")

    def test_create_returns_webhook(self):
        resource = _make_resource()
        result = resource.create("https://example.com/hook", ["link.created"])
        assert isinstance(result, Webhook)
        assert result.id == "wh1"

    def test_create_sends_correct_body(self):
        resource = _make_resource()
        resource.create(
            "https://example.com/hook",
            ["link.created"],
            name="My Webhook",
            secret="s3cr3t",
        )
        body = resource._http.post.call_args[1]["json"]
        assert body["url"] == "https://example.com/hook"
        assert body["events"] == ["link.created"]
        assert body["name"] == "My Webhook"
        assert body["secret"] == "s3cr3t"

    def test_create_without_optional_fields(self):
        resource = _make_resource()
        resource.create("https://example.com/hook", ["link.click"])
        body = resource._http.post.call_args[1]["json"]
        assert "name" not in body
        assert "secret" not in body

    def test_update_calls_patch(self):
        resource = _make_resource()
        resource.update("wh1", enabled=False)
        resource._http.patch.assert_called_once_with(
            "/api/webhooks/wh1", json={"enabled": False}
        )

    def test_update_returns_webhook(self):
        resource = _make_resource()
        result = resource.update("wh1", name="Renamed")
        assert isinstance(result, Webhook)

    def test_delete_calls_endpoint(self):
        resource = _make_resource()
        resource.delete("wh1")
        resource._http.delete.assert_called_once_with("/api/webhooks/wh1")

    def test_test_calls_correct_endpoint(self):
        resource = _make_resource()
        resource._http.post.return_value = {"sent": True}
        resource.test("wh1", "link.created")
        resource._http.post.assert_called_once_with(
            "/api/webhooks/wh1/test", json={"eventType": "link.created"}
        )
