"""Unit tests for the Affiliate resource."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from awsysco.models import AffiliateProgram
from awsysco.resources.affiliate import AffiliateResource


_PROGRAM_DATA = {
    "id": "prog1",
    "name": "My Affiliate Program",
    "description": "Great program",
    "commissionType": "cpc",
    "cpcRate": 0.5,
    "cpaRate": None,
    "cookieDays": 30,
    "status": "active",
}


def _make_resource():
    http = MagicMock()
    http.post.return_value = _PROGRAM_DATA
    http.get.return_value = [_PROGRAM_DATA]
    http.patch.return_value = _PROGRAM_DATA
    http.delete.return_value = None
    return AffiliateResource(http)


class TestAffiliatePrograms:
    def test_create_program_calls_endpoint(self):
        resource = _make_resource()
        resource.create_program("My Program", "cpc", cpc_rate=0.5)
        resource._http.post.assert_called_once()
        body = resource._http.post.call_args[1]["json"]
        assert body["name"] == "My Program"
        assert body["commissionType"] == "cpc"
        assert body["cpcRate"] == 0.5

    def test_create_program_returns_affiliate_program(self):
        resource = _make_resource()
        result = resource.create_program("My Program", "cpc")
        assert isinstance(result, AffiliateProgram)
        assert result.id == "prog1"

    def test_list_programs_calls_endpoint(self):
        resource = _make_resource()
        resource.list_programs()
        resource._http.get.assert_called_once_with("/api/affiliate/programs")

    def test_list_programs_returns_list(self):
        resource = _make_resource()
        result = resource.list_programs()
        assert isinstance(result, list)
        assert all(isinstance(p, AffiliateProgram) for p in result)

    def test_list_programs_handles_dict_wrapper(self):
        resource = _make_resource()
        resource._http.get.return_value = {"programs": [_PROGRAM_DATA]}
        result = resource.list_programs()
        assert len(result) == 1

    def test_get_program_calls_endpoint(self):
        resource = _make_resource()
        resource._http.get.return_value = _PROGRAM_DATA
        resource.get_program("prog1")
        resource._http.get.assert_called_once_with("/api/affiliate/programs/prog1")

    def test_get_program_returns_affiliate_program(self):
        resource = _make_resource()
        resource._http.get.return_value = _PROGRAM_DATA
        result = resource.get_program("prog1")
        assert isinstance(result, AffiliateProgram)

    def test_update_program_maps_fields(self):
        resource = _make_resource()
        resource.update_program("prog1", cpc_rate=1.0, cookie_days=60)
        body = resource._http.patch.call_args[1]["json"]
        assert body["cpcRate"] == 1.0
        assert body["cookieDays"] == 60

    def test_get_program_stats_calls_endpoint(self):
        resource = _make_resource()
        resource._http.get.return_value = {"clicks": 100}
        resource.get_program_stats("prog1")
        resource._http.get.assert_called_once_with(
            "/api/affiliate/programs/prog1/stats", params={"period": "30d"}
        )

    def test_list_partners_calls_endpoint(self):
        resource = _make_resource()
        resource._http.get.return_value = []
        resource.list_partners("prog1")
        resource._http.get.assert_called_once_with(
            "/api/affiliate/programs/prog1/partners"
        )

    def test_update_partner_status_calls_patch(self):
        resource = _make_resource()
        resource.update_partner_status("prog1", "partner1", "approved")
        resource._http.patch.assert_called_once_with(
            "/api/affiliate/programs/prog1/partners/partner1",
            json={"status": "approved"},
        )

    def test_discover_calls_endpoint(self):
        resource = _make_resource()
        resource.discover()
        resource._http.get.assert_called_once_with(
            "/api/affiliate/discover", params={"limit": 20}
        )

    def test_discover_custom_limit(self):
        resource = _make_resource()
        resource.discover(limit=5)
        resource._http.get.assert_called_once_with(
            "/api/affiliate/discover", params={"limit": 5}
        )

    def test_join_calls_endpoint(self):
        resource = _make_resource()
        resource._http.post.return_value = {"joined": True}
        resource.join("prog1")
        resource._http.post.assert_called_once_with(
            "/api/affiliate/join/prog1", json={}
        )

    def test_join_with_partner_code(self):
        resource = _make_resource()
        resource._http.post.return_value = {"joined": True}
        resource.join("prog1", partner_code="CODE123")
        body = resource._http.post.call_args[1]["json"]
        assert body["partnerCode"] == "CODE123"

    def test_list_partnerships_calls_endpoint(self):
        resource = _make_resource()
        resource._http.get.return_value = []
        resource.list_partnerships()
        resource._http.get.assert_called_once_with("/api/affiliate/partnerships")

    def test_get_partnership_stats_calls_endpoint(self):
        resource = _make_resource()
        resource._http.get.return_value = {}
        resource.get_partnership_stats("p1")
        resource._http.get.assert_called_once_with(
            "/api/affiliate/partnerships/p1/stats", params={"period": "30d"}
        )

    def test_leave_program_calls_delete(self):
        resource = _make_resource()
        resource.leave_program("p1")
        resource._http.delete.assert_called_once_with("/api/affiliate/partnerships/p1")

    def test_get_limits_calls_endpoint(self):
        resource = _make_resource()
        resource._http.get.return_value = {"maxPrograms": 3}
        resource.get_limits()
        resource._http.get.assert_called_once_with("/api/affiliate/limits")
