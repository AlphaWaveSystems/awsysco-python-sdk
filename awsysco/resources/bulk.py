"""Bulk resource — create multiple links in one request."""

from __future__ import annotations

from typing import Any, Dict, List

from .._http import HttpClient
from ..models import BulkResult


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
        # Map snake_case keys to camelCase for the API
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

        data = self._http.post("/api/v1/bulk", json={"urls": payload})
        return BulkResult.model_validate(data)
