"""Bulk resource — create multiple links in one request."""

from __future__ import annotations

from typing import Any, Dict, List

from .._http import HttpClient
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


class BulkResource:
    """Interact with /api/v1/bulk."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def create(self, urls: List[Dict[str, Any]]) -> BulkResult:
        """Bulk-create multiple shortened links.

        Args:
            urls: A list of link dicts. Each dict must have a ``url`` key and
                  may optionally include ``custom_slug``, ``expires_at``, and
                  ``max_clicks``.

                  Example::

                      [
                          {"url": "https://example.com"},
                          {"url": "https://other.com", "custom_slug": "other"},
                      ]

        Returns:
            A BulkResult with created/failed counts and per-URL results.
        """
        payload = [_normalize_bulk_item(item) for item in urls]

        data = self._http.post("/api/v1/bulk", json={"urls": payload})
        # Normalise: API sometimes wraps counts under a "summary" key
        if isinstance(data, dict) and "summary" in data and "created" not in data:
            summary = data["summary"]
            data = dict(data)
            data.setdefault("created", summary.get("created"))
            data.setdefault("failed", summary.get("failed"))
        return BulkResult.model_validate(data)
