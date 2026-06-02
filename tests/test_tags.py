"""Unit tests for the Tags resource."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from awsysco.resources.tags import TagsResource


def _make_resource(return_value=None):
    http = MagicMock()
    http.post.return_value = return_value or {"ok": True}
    http.delete.return_value = return_value or {"ok": True}
    return TagsResource(http)


class TestTagsAdd:
    def test_add_calls_correct_endpoint(self):
        resource = _make_resource()
        resource.add("abc123", "promo")
        resource._http.post.assert_called_once_with(
            "/api/link/abc123/tags", json={"tag": "promo"}
        )

    def test_add_returns_dict(self):
        resource = _make_resource({"tag": "promo", "ok": True})
        result = resource.add("abc123", "promo")
        assert isinstance(result, dict)

    def test_add_encodes_short_path(self):
        resource = _make_resource()
        resource.add("ns/slug", "test")
        resource._http.post.assert_called_once_with(
            "/api/link/ns%2Fslug/tags", json={"tag": "test"}
        )

    def test_add_returns_empty_dict_on_none(self):
        http = MagicMock()
        http.post.return_value = None
        resource = TagsResource(http)
        result = resource.add("abc", "tag")
        assert result == {}


class TestTagsRemove:
    def test_remove_calls_correct_endpoint(self):
        resource = _make_resource()
        resource.remove("abc123", "promo")
        resource._http.delete.assert_called_once_with(
            "/api/link/abc123/tags/promo"
        )

    def test_remove_encodes_tag(self):
        resource = _make_resource()
        resource.remove("abc123", "hello world")
        resource._http.delete.assert_called_once_with(
            "/api/link/abc123/tags/hello%20world"
        )

    def test_remove_returns_dict(self):
        resource = _make_resource({"removed": True})
        result = resource.remove("abc123", "promo")
        assert isinstance(result, dict)
