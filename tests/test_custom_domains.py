"""Unit tests for the Custom Domains resource."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from awsysco.models import CustomDomain
from awsysco.resources.custom_domains import CustomDomainsResource


_DOMAIN_DATA = {
    "domain": "links.example.com",
    "status": "active",
    "verificationToken": "abc123",
    "isDefault": False,
    "linkCount": 0,
    "createdAt": "2026-01-01T00:00:00Z",
}


def _make_resource():
    http = MagicMock()
    http.get.return_value = {"domains": [_DOMAIN_DATA]}
    http.post.return_value = _DOMAIN_DATA
    http.patch.return_value = _DOMAIN_DATA
    http.delete.return_value = None
    return CustomDomainsResource(http)


class TestCustomDomains:
    def test_list_calls_endpoint(self):
        resource = _make_resource()
        resource.list()
        resource._http.get.assert_called_once_with("/api/user/domains")

    def test_add_calls_endpoint(self):
        resource = _make_resource()
        resource.add("links.example.com")
        resource._http.post.assert_called_once_with(
            "/api/user/domains", json={"domain": "links.example.com"}
        )

    def test_verify_calls_correct_endpoint(self):
        resource = _make_resource()
        resource._http.get.return_value = {"verified": True}
        resource.verify("links.example.com")
        resource._http.get.assert_called_once_with(
            "/api/user/domains/links.example.com/verify"
        )

    def test_activate_calls_correct_endpoint(self):
        resource = _make_resource()
        resource.activate("links.example.com")
        resource._http.post.assert_called_once_with(
            "/api/user/domains/links.example.com/activate"
        )

    def test_activate_returns_custom_domain(self):
        resource = _make_resource()
        result = resource.activate("links.example.com")
        assert isinstance(result, CustomDomain)
        assert result.domain == "links.example.com"

    def test_update_sends_is_default(self):
        resource = _make_resource()
        resource.update("links.example.com", is_default=True)
        body = resource._http.patch.call_args[1]["json"]
        assert body["isDefault"] is True

    def test_update_sends_not_found_html(self):
        resource = _make_resource()
        resource.update("links.example.com", not_found_html="<h1>404</h1>")
        body = resource._http.patch.call_args[1]["json"]
        assert body["notFoundHtml"] == "<h1>404</h1>"

    def test_update_returns_custom_domain(self):
        resource = _make_resource()
        result = resource.update("links.example.com", is_default=True)
        assert isinstance(result, CustomDomain)

    def test_remove_calls_delete(self):
        resource = _make_resource()
        resource.remove("links.example.com")
        resource._http.delete.assert_called_once_with(
            "/api/user/domains/links.example.com"
        )

    def test_check_calls_correct_endpoint(self):
        resource = _make_resource()
        resource._http.get.return_value = {"available": True}
        resource.check("links.example.com")
        resource._http.get.assert_called_once_with(
            "/api/domains/check/links.example.com"
        )
