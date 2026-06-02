"""Async Saved Views resource."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._async_http import AsyncHttpClient
from ..models import SavedView


class AsyncSavedViewsResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def list(self) -> List[SavedView]:
        data = await self._http.get("/api/views")
        if isinstance(data, list):
            return [SavedView.model_validate(item) for item in data]
        items = data.get("views", []) if isinstance(data, dict) else []
        return [SavedView.model_validate(item) for item in items]

    async def create(self, name: str, filters: Dict[str, Any]) -> SavedView:
        data = await self._http.post("/api/views", json={"name": name, "filters": filters})
        return SavedView.model_validate(data)

    async def update(self, view_id: str, *, name: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> SavedView:
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if filters is not None:
            body["filters"] = filters
        data = await self._http.patch(f"/api/views/{view_id}", json=body)
        return SavedView.model_validate(data)

    async def delete(self, view_id: str) -> None:
        await self._http.delete(f"/api/views/{view_id}")
