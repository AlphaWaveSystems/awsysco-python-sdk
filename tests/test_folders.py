"""Integration tests for the Folders resource."""

import time

from awsysco import Client
from awsysco.models import Folder, FolderList


def _folder_name() -> str:
    return f"SDK Test Folder {int(time.time() * 1000)}"


def _unique_url() -> str:
    return f"https://example.com/sdk-folder-{int(time.time() * 1000)}"


class TestFolders:
    def test_create_folder(self, client: Client) -> None:
        folder = client.folders.create(_folder_name(), color="#FF5733")
        assert isinstance(folder, Folder)
        assert folder.id is not None
        # Clean up
        client.folders.delete(folder.id)

    def test_list_contains_created_folder(self, client: Client) -> None:
        name = _folder_name()
        folder = client.folders.create(name)
        assert folder.id is not None

        folder_list = client.folders.list()
        assert isinstance(folder_list, FolderList)
        ids = [f.id for f in folder_list.folders]
        assert folder.id in ids

        # Clean up
        client.folders.delete(folder.id)

    def test_assign_link_to_folder(self, client: Client) -> None:
        folder = client.folders.create(_folder_name())
        assert folder.id is not None

        link = client.links.create(_unique_url())
        assert link.short_code is not None

        # Should not raise
        client.folders.assign_link(link.short_code, folder.id)

        # Clean up
        client.folders.delete(folder.id)
        client.links.delete(link.short_code)

    def test_remove_link_from_folder(self, client: Client) -> None:
        folder = client.folders.create(_folder_name())
        assert folder.id is not None

        link = client.links.create(_unique_url())
        assert link.short_code is not None

        client.folders.assign_link(link.short_code, folder.id)
        # Remove — should not raise
        client.folders.remove_link(link.short_code)

        # Clean up
        client.folders.delete(folder.id)
        client.links.delete(link.short_code)

    def test_delete_folder(self, client: Client) -> None:
        folder = client.folders.create(_folder_name())
        assert folder.id is not None

        # Should not raise
        client.folders.delete(folder.id)
