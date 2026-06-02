"""Unit tests for the Saved Views resource."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from awsysco.models import SavedView
from awsysco.resources.saved_views import SavedViewsResource


_VIEW_DATA = {
    "id": "v1",
    "name": "My View",
    "filters": {"tag": "promo", "status": "active"},
    "createdAt": "2026-01-01T00:00:00Z",
}


def _make_resource():
    http = MagicMock()
    http.get.return_value = [_VIEW_DATA]
    http.post.return_value = _VIEW_DATA
    http.patch.return_value = _VIEW_DATA
    http.delete.return_value = None
    return SavedViewsResource(http)


class TestSavedViews:
    def test_list_calls_endpoint(self):
        resource = _make_resource()
        resource.list()
        resource._http.get.assert_called_once_with("/api/views")

    def test_list_returns_list_of_saved_views(self):
        resource = _make_resource()
        result = resource.list()
        assert isinstance(result, list)
        assert all(isinstance(v, SavedView) for v in result)

    def test_list_handles_dict_wrapper(self):
        resource = _make_resource()
        resource._http.get.return_value = {"views": [_VIEW_DATA]}
        result = resource.list()
        assert len(result) == 1
        assert isinstance(result[0], SavedView)

    def test_create_calls_endpoint(self):
        resource = _make_resource()
        resource.create("My View", {"tag": "promo"})
        resource._http.post.assert_called_once_with(
            "/api/views", json={"name": "My View", "filters": {"tag": "promo"}}
        )

    def test_create_returns_saved_view(self):
        resource = _make_resource()
        result = resource.create("My View", {})
        assert isinstance(result, SavedView)
        assert result.id == "v1"

    def test_update_calls_patch(self):
        resource = _make_resource()
        resource.update("v1", name="Renamed")
        resource._http.patch.assert_called_once_with(
            "/api/views/v1", json={"name": "Renamed"}
        )

    def test_update_with_filters(self):
        resource = _make_resource()
        resource.update("v1", filters={"status": "inactive"})
        body = resource._http.patch.call_args[1]["json"]
        assert body["filters"] == {"status": "inactive"}

    def test_update_returns_saved_view(self):
        resource = _make_resource()
        result = resource.update("v1", name="Renamed")
        assert isinstance(result, SavedView)

    def test_delete_calls_endpoint(self):
        resource = _make_resource()
        resource.delete("v1")
        resource._http.delete.assert_called_once_with("/api/views/v1")
