"""Async Links resource."""

from __future__ import annotations

from typing import Any, AsyncIterator, Dict, List, Optional, Union
from urllib.parse import quote

from .._async_http import AsyncHttpClient
from ..models import GeoRestriction, Link, LinkList, OgMeta, RoutingRule

_MAX_PAGE_SIZE = 100


def _to_dict(value: Optional[Union[Dict[str, Any], Any]]) -> Optional[Dict[str, Any]]:
    """Accept either a plain dict or one of the typed request models."""
    if value is None or isinstance(value, dict):
        return value
    return value.model_dump(by_alias=True, exclude_none=True)


class AsyncLinksResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(
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
        data = await self._http.post("/api/v1/links", json=body)
        return Link.model_validate(data)

    async def list(self, *, limit: int = 20, offset: int = 0) -> LinkList:
        limit = max(1, min(limit, _MAX_PAGE_SIZE))
        data = await self._http.get("/api/v1/links", params={"limit": limit, "offset": offset})
        return LinkList.model_validate(data)

    async def list_all(self, *, limit: int = 100) -> AsyncIterator[Link]:
        """Async-iterate over every link, auto-paginating with ``limit``/``offset``.

        Stops when the platform reports ``has_more=False``, or a page comes back
        shorter than ``limit`` (including empty).
        """
        limit = max(1, min(limit, _MAX_PAGE_SIZE))
        offset = 0
        while True:
            page = await self.list(limit=limit, offset=offset)
            for link in page.links:
                yield link
            if page.has_more is False:
                return
            if len(page.links) < limit:
                return
            offset += limit

    async def get(self, short_path: str) -> Link:
        data = await self._http.get(f"/api/v1/links/{short_path}")
        return Link.model_validate(data)

    async def update(
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
        data = await self._http.patch(
            f"/api/v1/links/{quote(short_path, safe='')}", json=body
        )
        return Link.model_validate(data)

    async def delete(self, short_path: str) -> None:
        await self._http.delete(f"/api/v1/links/{short_path}")
