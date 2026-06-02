"""Async Bulk resource."""

from __future__ import annotations

from typing import Any, Dict, List

from .._async_http import AsyncHttpClient
from ..models import BulkResult


class AsyncBulkResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(self, urls: List[Dict[str, Any]]) -> BulkResult:
        payload: List[Dict[str, Any]] = []
        for item in urls:
            entry: Dict[str, Any] = {"url": item["url"]}
            if "custom_slug" in item:
                entry["customSlug"] = item["custom_slug"]
            if "customSlug" in item:
                entry["customSlug"] = item["customSlug"]
            if "expires_at" in item:
                entry["expiresAt"] = item["expires_at"]
            if "expiresAt" in item:
                entry["expiresAt"] = item["expiresAt"]
            if "max_clicks" in item:
                entry["maxClicks"] = item["max_clicks"]
            if "maxClicks" in item:
                entry["maxClicks"] = item["maxClicks"]
            payload.append(entry)
        data = await self._http.post("/api/v1/bulk", json={"urls": payload})
        return BulkResult.model_validate(data)
