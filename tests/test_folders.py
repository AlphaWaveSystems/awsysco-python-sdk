"""Tests for the Folders resource."""

from __future__ import annotations

import time
from unittest.mock import MagicMock

from awsysco import Client
from awsysco.models import Folder, FolderList
from awsysco.resources.folders import FoldersResource


# ---------------------------------------------------------------------------
# Unit tests — no network required
# ---------------------------------------------------------------------------

_FOLDER_DATA = {
    "id": "folder1",
    "name": "Test Folder",
    "color": "#FF5733",
    "linkCount": 0,
    "createdAt": "2026-01-01T00:00:00Z",
}


def _make_resource():
    http = MagicMock()
    http.get.return_value = {"folders": [_FOLDER_DATA], "limit": 10, "used": 1}
    http.post.return_value = _FOLDER_DATA
    http.patch.return_value = _FOLDER_DATA
    http.delete.return_value = None
    return FoldersResource(http)


class TestFoldersUnit:
    def test_update_calls_patch_endpoint(self):
        resource = _make_resource()
        resource.update("folder1", name="Renamed")
        resource._http.patch.assert_called_once_with(
            "/api/v1/folders/folder1", json={"name": "Renamed"}
        )

    def test_update_sends_color(self):
        resource = _make_resource()
        resource.update("folder1", color="#0000FF")
        body = resource._http.patch.call_args[1]["json"]
        assert body["color"] == "#0000FF"

    def test_update_returns_folder(self):
        resource = _make_resource()
        result = resource.update("folder1", name="New Name")
        assert isinstance(result, Folder)

    def test_update_omits_none_fields(self):
        resource = _make_resource()
        resource.update("folder1", name="Name Only")
        body = resource._http.patch.call_args[1]["json"]
        assert "color" not in body

    def test_create_calls_endpoint(self):
        resource = _make_resource()
        resource.create("My Folder", color="#AABBCC")
        body = resource._http.post.call_args[1]["json"]
        assert body["name"] == "My Folder"
        assert body["color"] == "#AABBCC"

    def test_list_calls_endpoint(self):
        resource = _make_resource()
        resource.list()
        resource._http.get.assert_called_once_with("/api/v1/folders")


# ---------------------------------------------------------------------------
# Integration tests — require AWSYS_API_KEY
# ---------------------------------------------------------------------------


def _folder_name() -> str:
    return f"SDK Test Folder {int(time.time() * 1000)}"


def _unique_url() -> str:
    return f"https://example.com/sdk-folder-{int(time.time() * 1000)}"


class TestFolders:
    def test_create_folder(self, client: Client) -> None:
        folder = client.folders.create(_folder_name(), color="#FF5733")
        assert isinstance(folder, Folder)
        assert folder.id is not None
        client.folders.delete(folder.id)

    def test_list_contains_created_folder(self, client: Client) -> None:
        name = _folder_name()
        folder = client.folders.create(name)
        assert folder.id is not None

        folder_list = client.folders.list()
        assert isinstance(folder_list, FolderList)
        ids = [f.id for f in folder_list.folders]
        assert folder.id in ids
        client.folders.delete(folder.id)

    def test_assign_link_to_folder(self, client: Client) -> None:
        folder = client.folders.create(_folder_name())
        assert folder.id is not None

        link = client.links.create(_unique_url())
        assert link.short_code is not None

        client.folders.assign_link(link.short_code, folder.id)

        client.folders.delete(folder.id)
        client.links.delete(link.short_code)

    def test_remove_link_from_folder(self, client: Client) -> None:
        folder = client.folders.create(_folder_name())
        assert folder.id is not None

        link = client.links.create(_unique_url())
        assert link.short_code is not None

        client.folders.assign_link(link.short_code, folder.id)
        client.folders.remove_link(link.short_code)

        client.folders.delete(folder.id)
        client.links.delete(link.short_code)

    def test_delete_folder(self, client: Client) -> None:
        folder = client.folders.create(_folder_name())
        assert folder.id is not None
        client.folders.delete(folder.id)
