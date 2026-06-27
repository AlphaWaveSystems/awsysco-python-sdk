"""Unit tests for the Imports resource (sync + async). Fully mocked."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from awsysco.async_resources.imports import AsyncImportsResource
from awsysco.models import ImportJob
from awsysco.resources.imports import ImportsResource

_JOB_ID = "imp_abc123"


def _job_payload(status="pending"):
    return {
        "id": _JOB_ID,
        "userId": "user_42",
        "provider": "bitly",
        "status": status,
        "scanOnly": False,
        "targetNamespace": "acme",
        "scopeFilter": None,
        "counts": {
            "fetched": 100,
            "transformed": 100,
            "written": 95,
            "errored": 5,
        },
        "errors": ["link 12 failed: invalid slug"],
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-01T00:05:00Z",
    }


def _make_resource():
    http = MagicMock()
    http.post.return_value = _job_payload()
    http.get.return_value = _job_payload()
    http.delete.return_value = _job_payload(status="cancelled")
    return ImportsResource(http)


class TestImportsSync:
    def test_start_posts_snake_case_body(self):
        resource = _make_resource()
        resource.start(
            provider="bitly",
            access_token="tok_123",
            target_namespace="acme",
            scan_only=True,
        )
        resource._http.post.assert_called_once_with(
            "/api/v1/imports",
            json={
                "provider": "bitly",
                "access_token": "tok_123",
                "target_namespace": "acme",
                "scan_only": True,
            },
        )

    def test_start_omits_none_optionals(self):
        resource = _make_resource()
        resource.start(provider="bitly", access_token="tok_123")
        resource._http.post.assert_called_once_with(
            "/api/v1/imports",
            json={"provider": "bitly", "access_token": "tok_123"},
        )

    def test_start_returns_import_job(self):
        result = _make_resource().start(provider="bitly", access_token="tok")
        assert isinstance(result, ImportJob)
        assert result.id == _JOB_ID
        assert result.provider == "bitly"
        assert result.counts.written == 95
        assert result.counts.errored == 5
        assert result.errors == ["link 12 failed: invalid slug"]

    def test_get_status_calls_endpoint(self):
        resource = _make_resource()
        resource.get_status(_JOB_ID)
        resource._http.get.assert_called_once_with(f"/api/v1/imports/{_JOB_ID}")

    def test_get_status_encodes_job_id(self):
        resource = _make_resource()
        resource.get_status("ns/slug")
        resource._http.get.assert_called_once_with("/api/v1/imports/ns%2Fslug")

    def test_cancel_calls_delete(self):
        resource = _make_resource()
        result = resource.cancel(_JOB_ID)
        resource._http.delete.assert_called_once_with(f"/api/v1/imports/{_JOB_ID}")
        assert isinstance(result, ImportJob)
        assert result.status == "cancelled"

    def test_list_unwraps_jobs_key(self):
        resource = _make_resource()
        resource._http.get.return_value = {"jobs": [_job_payload(), _job_payload()]}
        result = resource.list()
        resource._http.get.assert_called_once_with("/api/v1/imports", params=None)
        assert len(result) == 2
        assert all(isinstance(j, ImportJob) for j in result)

    def test_list_with_limit(self):
        resource = _make_resource()
        resource._http.get.return_value = {"jobs": []}
        resource.list(limit=5)
        resource._http.get.assert_called_once_with(
            "/api/v1/imports", params={"limit": 5}
        )

    def test_wait_for_completion_resolves_on_terminal(self):
        resource = _make_resource()
        # pending -> running -> completed
        resource._http.get.side_effect = [
            _job_payload(status="pending"),
            _job_payload(status="running"),
            _job_payload(status="completed"),
        ]
        result = resource.wait_for_completion(_JOB_ID, poll_interval=0.0, timeout=5.0)
        assert result.status == "completed"
        assert resource._http.get.call_count == 3

    def test_wait_for_completion_times_out(self):
        resource = _make_resource()
        resource._http.get.return_value = _job_payload(status="running")
        with pytest.raises(TimeoutError):
            resource.wait_for_completion(_JOB_ID, poll_interval=0.0, timeout=0.0)


def _make_async_resource():
    http = MagicMock()
    http.post = AsyncMock(return_value=_job_payload())
    http.get = AsyncMock(return_value=_job_payload())
    http.delete = AsyncMock(return_value=_job_payload(status="cancelled"))
    return AsyncImportsResource(http)


class TestImportsAsync:
    def test_start_posts_snake_case_body(self):
        resource = _make_async_resource()
        asyncio.run(
            resource.start(
                provider="bitly", access_token="tok_123", scan_only=True
            )
        )
        resource._http.post.assert_awaited_once_with(
            "/api/v1/imports",
            json={
                "provider": "bitly",
                "access_token": "tok_123",
                "scan_only": True,
            },
        )

    def test_start_returns_import_job(self):
        resource = _make_async_resource()
        result = asyncio.run(resource.start(provider="bitly", access_token="tok"))
        assert isinstance(result, ImportJob)
        assert result.counts.fetched == 100

    def test_get_status_calls_endpoint(self):
        resource = _make_async_resource()
        asyncio.run(resource.get_status(_JOB_ID))
        resource._http.get.assert_awaited_once_with(f"/api/v1/imports/{_JOB_ID}")

    def test_cancel_calls_delete(self):
        resource = _make_async_resource()
        result = asyncio.run(resource.cancel(_JOB_ID))
        resource._http.delete.assert_awaited_once_with(f"/api/v1/imports/{_JOB_ID}")
        assert result.status == "cancelled"

    def test_list_unwraps_jobs_key(self):
        resource = _make_async_resource()
        resource._http.get = AsyncMock(return_value={"jobs": [_job_payload()]})
        result = asyncio.run(resource.list())
        assert len(result) == 1
        assert isinstance(result[0], ImportJob)

    def test_wait_for_completion_resolves_on_terminal(self):
        resource = _make_async_resource()
        resource._http.get = AsyncMock(
            side_effect=[
                _job_payload(status="pending"),
                _job_payload(status="completed"),
            ]
        )
        result = asyncio.run(
            resource.wait_for_completion(_JOB_ID, poll_interval=0.0, timeout=5.0)
        )
        assert result.status == "completed"
        assert resource._http.get.await_count == 2

    def test_wait_for_completion_times_out(self):
        resource = _make_async_resource()
        resource._http.get = AsyncMock(return_value=_job_payload(status="running"))
        with pytest.raises(TimeoutError):
            asyncio.run(
                resource.wait_for_completion(
                    _JOB_ID, poll_interval=0.0, timeout=0.0
                )
            )
