"""Links resource — CRUD for shortened links."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._http import HttpClient
from ..models import GeoRestriction, Link, LinkList, OgMeta, RoutingRule


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
        routing_rules: Optional[List[Dict[str, str]]] = None,
        og_meta: Optional[Dict[str, str]] = None,
        geo_restriction: Optional[Dict[str, List[str]]] = None,
        password: Optional[str] = None,
        pass_ad_click_ids: Optional[bool] = None,
        folder_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Link:
        """Create a new shortened link.

        Args:
            url: The long URL to shorten.
            custom_slug: Optional custom short slug.
            expires_at: Optional expiry datetime (ISO 8601).
            max_clicks: Optional maximum click limit.
            routing_rules: Optional list of geo-routing rules, each with
                ``country`` and ``redirect_url`` keys.
            og_meta: Optional Open Graph metadata dict with ``title``,
                ``description``, and/or ``image`` keys.
            geo_restriction: Optional dict with ``allowed_countries`` and/or
                ``blocked_countries`` lists.
            password: Optional password to protect the link.
            pass_ad_click_ids: Whether to pass through ad click IDs (gclid etc).
            folder_id: Optional folder ID to assign the link to.
            tags: Optional list of tag strings.

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
        if routing_rules is not None:
            body["routingRules"] = routing_rules
        if og_meta is not None:
            body["ogMeta"] = og_meta
        if geo_restriction is not None:
            body["geoRestriction"] = geo_restriction
        if password is not None:
            body["password"] = password
        if pass_ad_click_ids is not None:
            body["passAdClickIds"] = pass_ad_click_ids
        if folder_id is not None:
            body["folderId"] = folder_id
        if tags is not None:
            body["tags"] = tags

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
        url: Optional[str] = None,
        expires_at: Optional[str] = None,
        max_clicks: Optional[int] = None,
        routing_rules: Optional[List[Dict[str, str]]] = None,
        og_meta: Optional[Dict[str, str]] = None,
        geo_restriction: Optional[Dict[str, List[str]]] = None,
        password: Optional[str] = None,
        pass_ad_click_ids: Optional[bool] = None,
        folder_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Link:
        """Update a link's settings.

        Args:
            short_path: The short code or slug identifying the link.
            url: New destination URL.
            expires_at: New expiry datetime (ISO 8601), or None to clear.
            max_clicks: New maximum click limit, or None to clear.
            routing_rules: New list of geo-routing rules.
            og_meta: New Open Graph metadata.
            geo_restriction: New geo-restriction settings.
            password: New password (or empty string to remove).
            pass_ad_click_ids: Whether to pass through ad click IDs.
            folder_id: New folder ID.
            tags: New list of tags.

        Returns:
            The updated Link object.
        """
        body: Dict[str, Any] = {}
        if url is not None:
            body["url"] = url
        if expires_at is not None:
            body["expiresAt"] = expires_at
        if max_clicks is not None:
            body["maxClicks"] = max_clicks
        if routing_rules is not None:
            body["routingRules"] = routing_rules
        if og_meta is not None:
            body["ogMeta"] = og_meta
        if geo_restriction is not None:
            body["geoRestriction"] = geo_restriction
        if password is not None:
            body["password"] = password
        if pass_ad_click_ids is not None:
            body["passAdClickIds"] = pass_ad_click_ids
        if folder_id is not None:
            body["folderId"] = folder_id
        if tags is not None:
            body["tags"] = tags

        data = self._http.patch(f"/api/v1/links/{short_path}", json=body)
        return Link.model_validate(data)

    def delete(self, short_path: str) -> None:
        """Delete a link.

        Args:
            short_path: The short code or slug identifying the link.
        """
        self._http.delete(f"/api/v1/links/{short_path}")
