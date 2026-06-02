"""Unit tests for the UTM Templates resource."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from awsysco.models import UtmTemplate
from awsysco.resources.utm_templates import UtmTemplatesResource


def _make_resource(me_response=None):
    http = MagicMock()
    if me_response is not None:
        http.get.return_value = me_response
    else:
        http.get.return_value = {
            "uid": "user1",
            "utmTemplates": [
                {"id": "t1", "name": "Google Ads", "source": "google", "medium": "cpc", "campaign": "brand"},
            ],
        }
    http.post.return_value = {"id": "t2", "name": "New"}
    http.delete.return_value = None
    return UtmTemplatesResource(http)


class TestUtmTemplates:
    def test_list_calls_me_endpoint(self):
        resource = _make_resource()
        resource.list()
        resource._http.get.assert_called_once_with("/api/v1/me")

    def test_list_returns_utm_templates(self):
        resource = _make_resource()
        result = resource.list()
        assert isinstance(result, list)
        assert all(isinstance(t, UtmTemplate) for t in result)

    def test_list_returns_empty_when_no_templates(self):
        resource = _make_resource(me_response={"uid": "user1"})
        result = resource.list()
        assert result == []

    def test_list_parses_template_fields(self):
        resource = _make_resource()
        result = resource.list()
        assert result[0].name == "Google Ads"
        assert result[0].source == "google"

    def test_create_calls_correct_endpoint(self):
        resource = _make_resource()
        resource.create("My Template", "google", "cpc", "brand")
        resource._http.post.assert_called_once()
        call_args = resource._http.post.call_args
        assert call_args[0][0] == "/api/user/utm-templates"

    def test_create_sends_correct_body(self):
        resource = _make_resource()
        resource.create("My Template", "google", "cpc", "brand", term="shoes", content="banner")
        body = resource._http.post.call_args[1]["json"]
        assert body["name"] == "My Template"
        assert body["source"] == "google"
        assert body["medium"] == "cpc"
        assert body["campaign"] == "brand"
        assert body["term"] == "shoes"
        assert body["content"] == "banner"

    def test_delete_calls_correct_endpoint(self):
        resource = _make_resource()
        resource.delete("t1")
        resource._http.delete.assert_called_once_with("/api/user/utm-templates/t1")
