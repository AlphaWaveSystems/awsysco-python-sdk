"""Folders resource — organize links into folders."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .._http import HttpClient
from ..models import Folder, FolderList


class FoldersResource:
    """Interact with /api/v1/folders and link-folder assignment."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(self) -> FolderList:
        """List all folders for the authenticated user.

        Returns:
            A FolderList containing the folders.
        """
        data = self._http.get("/api/v1/folders")
        return FolderList.model_validate(data)

    def create(self, name: str, *, color: Optional[str] = None) -> Folder:
        """Create a new folder.

        Args:
            name: Display name for the folder.
            color: Optional hex color string (e.g. '#FF5733').

        Returns:
            The created Folder object.
        """
        body: Dict[str, Any] = {"name": name}
        if color is not None:
            body["color"] = color

        data = self._http.post("/api/v1/folders", json=body)
        return Folder.model_validate(data)

    def delete(self, folder_id: str) -> None:
        """Delete a folder.

        Args:
            folder_id: The ID of the folder to delete.
        """
        self._http.delete(f"/api/v1/folders/{folder_id}")

    def assign_link(self, short_path: str, folder_id: str) -> None:
        """Assign a link to a folder.

        Args:
            short_path: The short code/slug of the link.
            folder_id: The ID of the target folder.
        """
        self._http.post(
            f"/api/v1/links/{short_path}/folder",
            json={"folderId": folder_id},
        )

    def remove_link(self, short_path: str) -> None:
        """Remove a link from its current folder.

        Args:
            short_path: The short code/slug of the link.
        """
        self._http.post(
            f"/api/v1/links/{short_path}/folder",
            json={"folderId": None},
        )
