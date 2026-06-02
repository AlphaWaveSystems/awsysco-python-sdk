"""Async UTM Templates resource."""

from __future__ import annotations

from typing import Any, Dict, List

from .._async_http import AsyncHttpClient
from ..models import UtmTemplate


class AsyncUtmTemplatesResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def list(self) -> List[UtmTemplate]:
        resp = await self._http.get("/api/v1/me")
        items = resp.get("utmTemplates", []) if isinstance(resp, dict) else []
        return [UtmTemplate.model_validate(item) for item in items]

    async def create(self, name: str, source: str, medium: str, campaign: str, *, term: str = "", content: str = "") -> dict:
        body: Dict[str, Any] = {
            "name": name, "source": source, "medium": medium,
            "campaign": campaign, "term": term, "content": content,
        }
        return await self._http.post("/api/user/utm-templates", json=body) or {}

    async def delete(self, template_id: str) -> dict:
        return await self._http.delete(f"/api/user/utm-templates/{template_id}") or {}
