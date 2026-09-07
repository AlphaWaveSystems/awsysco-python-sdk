"""Unit tests for the Profile resource (sync + async). Fully mocked."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

from awsysco.async_resources.profile import AsyncProfileResource
from awsysco.models import Profile
from awsysco.resources.profile import ProfileResource

_PROFILE_DATA = {
    "uid": "user_42",
    "email": "dev@example.com",
    "displayName": "Dev User",
    "createdAt": "2026-01-01T00:00:00Z",
}


def _make_resource():
    http = MagicMock()
    http.get.return_value = _PROFILE_DATA
    http.patch.return_value = _PROFILE_DATA
    return ProfileResource(http)


class TestProfileSync:
    def test_get_calls_endpoint(self):
        resource = _make_resource()
        resource.get()
        resource._http.get.assert_called_once_with("/api/user/profile")

    def test_get_returns_profile(self):
        resource = _make_resource()
        result = resource.get()
        assert isinstance(result, Profile)
        assert result.email == "dev@example.com"
        assert result.display_name == "Dev User"

    def test_update_calls_endpoint(self):
        resource = _make_resource()
        resource.update(display_name="New Name")
        resource._http.patch.assert_called_once_with(
            "/api/user/profile", json={"displayName": "New Name"}
        )

    def test_update_returns_profile(self):
        resource = _make_resource()
        result = resource.update(display_name="New Name")
        assert isinstance(result, Profile)


def _make_async_resource():
    http = MagicMock()
    http.get = AsyncMock(return_value=_PROFILE_DATA)
    http.patch = AsyncMock(return_value=_PROFILE_DATA)
    return AsyncProfileResource(http)


class TestProfileAsync:
    def test_get_calls_endpoint(self):
        resource = _make_async_resource()
        asyncio.run(resource.get())
        resource._http.get.assert_awaited_once_with("/api/user/profile")

    def test_get_returns_profile(self):
        resource = _make_async_resource()
        result = asyncio.run(resource.get())
        assert isinstance(result, Profile)
        assert result.uid == "user_42"

    def test_update_calls_endpoint(self):
        resource = _make_async_resource()
        asyncio.run(resource.update(display_name="New Name"))
        resource._http.patch.assert_awaited_once_with(
            "/api/user/profile", json={"displayName": "New Name"}
        )
