"""Async Bulk resource."""

from __future__ import annotations

from typing import Any, Dict, List

from .._async_http import AsyncHttpClient
from ..models import BulkResult

# Maps either the snake_case or camelCase key a caller might use to the wire key.
_KEY_ALIASES: Dict[str, str] = {
    "custom_slug": "customSlug",
    "customSlug": "customSlug",
    "expires_at": "expiresAt",
    "expiresAt": "expiresAt",
    "max_clicks": "maxClicks",
    "maxClicks": "maxClicks",
}


def _normalize_bulk_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Map a caller-supplied link dict (snake_case or camelCase) to the wire shape."""
    entry: Dict[str, Any] = {"url": item["url"]}
    for key, value in item.items():
        wire_key = _KEY_ALIASES.get(key)
        if wire_key is not None:
            entry[wire_key] = value
    return entry


class AsyncBulkResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(self, urls: List[Dict[str, Any]]) -> BulkResult:
        payload = [_normalize_bulk_item(item) for item in urls]
        data = await self._http.post("/api/v1/bulk", json={"urls": payload})
        # Normalise: API sometimes wraps counts under a "summary" key
        if isinstance(data, dict) and "summary" in data and "created" not in data:
            summary = data["summary"]
            data = dict(data)
            data.setdefault("created", summary.get("created"))
            data.setdefault("failed", summary.get("failed"))
        return BulkResult.model_validate(data)
