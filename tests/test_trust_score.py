"""Unit tests for the Trust Score resource."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from awsysco.models import TrustScoreResult
from awsysco.resources.trust_score import TrustScoreResource


def _make_resource(return_value=None):
    http = MagicMock()
    http.get.return_value = return_value or {
        "short": "abc123",
        "long": "https://example.com",
        "score": 0.95,
        "status": "safe",
        "threats": [],
        "scannedAt": "2026-01-01T00:00:00Z",
    }
    return TrustScoreResource(http)


class TestTrustScore:
    def test_scan_calls_correct_endpoint(self):
        resource = _make_resource()
        resource.scan("abc123")
        resource._http.get.assert_called_once_with("/api/link-scan/abc123")

    def test_scan_encodes_slash(self):
        resource = _make_resource()
        resource.scan("ns/slug")
        resource._http.get.assert_called_once_with("/api/link-scan/ns%2Fslug")

    def test_scan_returns_trust_score_result(self):
        resource = _make_resource()
        result = resource.scan("abc123")
        assert isinstance(result, TrustScoreResult)

    def test_scan_populates_score(self):
        resource = _make_resource()
        result = resource.scan("abc123")
        assert result.score == 0.95

    def test_scan_populates_status(self):
        resource = _make_resource()
        result = resource.scan("abc123")
        assert result.status == "safe"

    def test_scan_populates_threats(self):
        resource = _make_resource()
        result = resource.scan("abc123")
        assert result.threats == []
