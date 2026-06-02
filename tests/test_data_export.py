"""Unit tests for the Data Export resource."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from awsysco.resources.data_export import DataExportResource


def _make_resource(text="short_code,long_url\nabc,https://example.com"):
    http = MagicMock()
    http.get_text.return_value = text
    return DataExportResource(http)


class TestDataExport:
    def test_export_links_calls_correct_endpoint(self):
        resource = _make_resource()
        resource.export_links()
        resource._http.get_text.assert_called_once_with("/api/export/links")

    def test_export_links_returns_string(self):
        resource = _make_resource("col1,col2\nval1,val2")
        result = resource.export_links()
        assert isinstance(result, str)
        assert "col1" in result

    def test_export_link_stats_calls_correct_endpoint(self):
        resource = _make_resource()
        resource.export_link_stats("abc123")
        resource._http.get_text.assert_called_once_with("/api/export/stats/abc123")

    def test_export_link_stats_returns_string(self):
        resource = _make_resource("date,clicks\n2026-01-01,42")
        result = resource.export_link_stats("abc123")
        assert isinstance(result, str)
        assert "clicks" in result
