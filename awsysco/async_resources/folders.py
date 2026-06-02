"""Async Folders resource."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .._async_http import AsyncHttpClient
from ..models import Folder, FolderList


class AsyncFoldersResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def list(self) -> FolderList:
        data = await self._http.get("/api/v1/folders")
        return FolderList.model_validate(data)

    async def create(self, name: str, *, color: Optional[str] = None) -> Folder:
        body: Dict[str, Any] = {"name": name}
        if color is not None:
            body["color"] = color
        data = await self._http.post("/api/v1/folders", json=body)
        return Folder.model_validate(data)

    async def update(self, folder_id: str, *, name: Optional[str] = None, color: Optional[str] = None) -> Folder:
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if color is not None:
            body["color"] = color
        data = await self._http.patch(f"/api/v1/folders/{folder_id}", json=body)
        return Folder.model_validate(data)

    async def delete(self, folder_id: str) -> None:
        await self._http.delete(f"/api/v1/folders/{folder_id}")

    async def assign_link(self, short_path: str, folder_id: str) -> None:
        await self._http.post(f"/api/v1/links/{short_path}/folder", json={"folderId": folder_id})

    async def remove_link(self, short_path: str) -> None:
        await self._http.post(f"/api/v1/links/{short_path}/folder", json={"folderId": None})
