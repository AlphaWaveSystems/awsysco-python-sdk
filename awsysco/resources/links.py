"""Links resource — CRUD for shortened links."""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Optional, Union
from urllib.parse import quote

from .._http import HttpClient
from ..models import GeoRestriction, Link, LinkList, OgMeta, RoutingRule

_MAX_PAGE_SIZE = 100


def _to_dict(value: Optional[Union[Dict[str, Any], Any]]) -> Optional[Dict[str, Any]]:
    """Accept either a plain dict or one of the typed request models."""
    if value is None or isinstance(value, dict):
        return value
    return value.model_dump(by_alias=True, exclude_none=True)


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
        routing_rules: Optional[List[Union[Dict[str, str], RoutingRule]]] = None,
        og_meta: Optional[Union[Dict[str, str], OgMeta]] = None,
        geo_restriction: Optional[Union[Dict[str, List[str]], GeoRestriction]] = None,
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
            routing_rules: Optional list of geo-routing rules — each either a
                :class:`~awsysco.models.RoutingRule` or a dict with ``country`` and
                ``redirect_url`` keys.
            og_meta: Optional Open Graph metadata — an :class:`~awsysco.models.OgMeta` or
                a dict with ``title``, ``description``, and/or ``image`` keys.
            geo_restriction: Optional geo-restriction settings — a
                :class:`~awsysco.models.GeoRestriction` or a dict with
                ``allowed_countries``/``blocked_countries`` lists.
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
            body["routingRules"] = [_to_dict(rule) for rule in routing_rules]
        if og_meta is not None:
            body["ogMeta"] = _to_dict(og_meta)
        if geo_restriction is not None:
            body["geoRestriction"] = _to_dict(geo_restriction)
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
            limit: Number of results (default 20, platform max 100 — clamped
                client-side).
            offset: Pagination offset (default 0).

        Returns:
            A LinkList containing links and pagination info.
        """
        limit = max(1, min(limit, _MAX_PAGE_SIZE))
        data = self._http.get("/api/v1/links", params={"limit": limit, "offset": offset})
        return LinkList.model_validate(data)

    def list_all(self, *, limit: int = 100) -> Iterator[Link]:
        """Iterate over every link, auto-paginating with ``limit``/``offset``.

        Stops when the platform reports ``has_more=False``, or a page comes back
        shorter than ``limit`` (including empty), which guards against a missing
        ``has_more`` in the response.

        Args:
            limit: Page size to request (platform max 100 — clamped client-side).

        Yields:
            Each Link across every page.
        """
        limit = max(1, min(limit, _MAX_PAGE_SIZE))
        offset = 0
        while True:
            page = self.list(limit=limit, offset=offset)
            yield from page.links
            if page.has_more is False:
                return
            if len(page.links) < limit:
                return
            offset += limit

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
        routing_rules: Optional[List[Union[Dict[str, str], RoutingRule]]] = None,
        og_meta: Optional[Union[Dict[str, str], OgMeta]] = None,
        geo_restriction: Optional[Union[Dict[str, List[str]], GeoRestriction]] = None,
        password: Optional[str] = None,
        pass_ad_click_ids: Optional[bool] = None,
        folder_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Link:
        """Update a link's settings.

        Note: per the platform contract, ``PATCH /api/v1/links/:shortPath`` cannot
        address a namespaced link (``prefix/slug``) — the slash is URL-encoded here,
        but updating a namespaced link's settings currently requires the platform fix.

        Args:
            short_path: The short code or slug identifying the link.
            url: New destination URL.
            expires_at: New expiry datetime (ISO 8601), or None to clear.
            max_clicks: New maximum click limit, or None to clear.
            routing_rules: New list of geo-routing rules (models or dicts).
            og_meta: New Open Graph metadata (a model or dict).
            geo_restriction: New geo-restriction settings (a model or dict).
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
            body["routingRules"] = [_to_dict(rule) for rule in routing_rules]
        if og_meta is not None:
            body["ogMeta"] = _to_dict(og_meta)
        if geo_restriction is not None:
            body["geoRestriction"] = _to_dict(geo_restriction)
        if password is not None:
            body["password"] = password
        if pass_ad_click_ids is not None:
            body["passAdClickIds"] = pass_ad_click_ids
        if folder_id is not None:
            body["folderId"] = folder_id
        if tags is not None:
            body["tags"] = tags

        data = self._http.patch(f"/api/v1/links/{quote(short_path, safe='')}", json=body)
        return Link.model_validate(data)

    def delete(self, short_path: str) -> None:
        """Delete a link.

        Args:
            short_path: The short code or slug identifying the link.
        """
        self._http.delete(f"/api/v1/links/{short_path}")
