"""Unit tests for the Namespace resource."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from awsysco.models import NamespaceCheckResult, NamespaceInfo
from awsysco.resources.namespace import NamespaceResource


def _make_resource():
    http = MagicMock()
    return NamespaceResource(http)


_NAMESPACE_INFO = {
    "hasAccess": True,
    "namespace": "myco",
    "tier": "pro",
    "upgradeRequired": False,
}

_CHECK_RESULT = {
    "namespace": "myco",
    "available": True,
    "reason": None,
    "previewUrl": "https://awsys.co/myco/test",
}


class TestNamespace:
    def test_get_calls_correct_endpoint(self):
        resource = _make_resource()
        resource._http.get.return_value = _NAMESPACE_INFO
        resource.get()
        resource._http.get.assert_called_once_with("/api/user/namespace")

    def test_get_returns_namespace_info(self):
        resource = _make_resource()
        resource._http.get.return_value = _NAMESPACE_INFO
        result = resource.get()
        assert isinstance(result, NamespaceInfo)
        assert result.namespace == "myco"

    def test_check_calls_correct_endpoint(self):
        resource = _make_resource()
        resource._http.get.return_value = _CHECK_RESULT
        resource.check("myco")
        resource._http.get.assert_called_once_with("/api/namespace/check/myco")

    def test_check_returns_check_result(self):
        resource = _make_resource()
        resource._http.get.return_value = _CHECK_RESULT
        result = resource.check("myco")
        assert isinstance(result, NamespaceCheckResult)
        assert result.available is True

    def test_claim_calls_correct_endpoint(self):
        resource = _make_resource()
        resource._http.post.return_value = _NAMESPACE_INFO
        resource.claim("myco")
        resource._http.post.assert_called_once_with(
            "/api/user/namespace", json={"namespace": "myco"}
        )

    def test_claim_returns_namespace_info(self):
        resource = _make_resource()
        resource._http.post.return_value = _NAMESPACE_INFO
        result = resource.claim("myco")
        assert isinstance(result, NamespaceInfo)

    def test_release_calls_delete(self):
        resource = _make_resource()
        resource._http.delete.return_value = None
        resource.release()
        resource._http.delete.assert_called_once_with("/api/user/namespace")

    def test_release_returns_dict(self):
        resource = _make_resource()
        resource._http.delete.return_value = None
        result = resource.release()
        assert isinstance(result, dict)
