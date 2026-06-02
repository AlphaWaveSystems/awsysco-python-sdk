"""Async Webhooks resource."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._async_http import AsyncHttpClient
from ..models import Webhook


class AsyncWebhooksResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def list_event_types(self) -> dict:
        return await self._http.get("/api/webhooks/event-types") or {}

    async def list(self) -> dict:
        return await self._http.get("/api/webhooks") or {}

    async def create(self, url: str, events: List[str], *, name: Optional[str] = None, secret: Optional[str] = None) -> Webhook:
        body: Dict[str, Any] = {"url": url, "events": events}
        if name is not None:
            body["name"] = name
        if secret is not None:
            body["secret"] = secret
        data = await self._http.post("/api/webhooks", json=body)
        return Webhook.model_validate(data)

    async def update(self, webhook_id: str, **kwargs: Any) -> Webhook:
        body: Dict[str, Any] = {}
        key_map = {"url": "url", "events": "events", "name": "name", "secret": "secret", "enabled": "enabled"}
        for k, v in kwargs.items():
            body[key_map.get(k, k)] = v
        data = await self._http.patch(f"/api/webhooks/{webhook_id}", json=body)
        return Webhook.model_validate(data)

    async def delete(self, webhook_id: str) -> dict:
        return await self._http.delete(f"/api/webhooks/{webhook_id}") or {}

    async def test(self, webhook_id: str, event_type: str) -> dict:
        return await self._http.post(f"/api/webhooks/{webhook_id}/test", json={"eventType": event_type}) or {}
