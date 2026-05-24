"""Links resource — CRUD for shortened links."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .._http import HttpClient
from ..models import Link, LinkList


class LinksResource:
    """Interact with /api/v1/links."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def create(
        self,
        url: str,
        *,
        custom_slug: Optional[str] = None,
        expires_at: Optional[str] = None,
        max_clicks: Optional[int] = None,
    ) -> Link:
        """Create a new shortened link.

        Args:
            url: The long URL to shorten.
            custom_slug: Optional custom short slug.
            expires_at: Optional expiry datetime (ISO 8601).
            max_clicks: Optional maximum click limit.

        Returns:
            The created Link object.
        """
        body: Dict[str, Any] = {"url": url}
        if custom_slug is not None:
            body["customSlug"] = custom_slug
        if expires_at is not None:
            body["expiresAt"] = expires_at
        if max_clicks is not None:
            body["maxClicks"] = max_clicks

        data = self._http.post("/api/v1/links", json=body)
        return Link.model_validate(data)

    def list(self, *, limit: int = 20, offset: int = 0) -> LinkList:
        """List links with pagination.

        Args:
            limit: Number of results (default 20).
            offset: Pagination offset (default 0).

        Returns:
            A LinkList containing links and pagination info.
        """
        data = self._http.get("/api/v1/links", params={"limit": limit, "offset": offset})
        return LinkList.model_validate(data)

    def get(self, short_path: str) -> Link:
        """Get a single link by its short path/code.

        Args:
            short_path: The short code or slug identifying the link.

        Returns:
            The Link object.
        """
        data = self._http.get(f"/api/v1/links/{short_path}")
        return Link.model_validate(data)

    def update(
        self,
        short_path: str,
        *,
        expires_at: Optional[str] = None,
        max_clicks: Optional[int] = None,
    ) -> Link:
        """Update a link's settings.

        Args:
            short_path: The short code or slug identifying the link.
            expires_at: New expiry datetime (ISO 8601), or None to clear.
            max_clicks: New maximum click limit, or None to clear.

        Returns:
            The updated Link object.
        """
        body: Dict[str, Any] = {}
        if expires_at is not None:
            body["expiresAt"] = expires_at
        if max_clicks is not None:
            body["maxClicks"] = max_clicks

        data = self._http.patch(f"/api/v1/links/{short_path}", json=body)
        return Link.model_validate(data)

    def delete(self, short_path: str) -> None:
        """Delete a link.

        Args:
            short_path: The short code or slug identifying the link.
        """
        self._http.delete(f"/api/v1/links/{short_path}")
