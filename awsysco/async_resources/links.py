"""Async Links resource."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._async_http import AsyncHttpClient
from ..models import Link, LinkList


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
        routing_rules: Optional[List[Dict[str, str]]] = None,
        og_meta: Optional[Dict[str, str]] = None,
        geo_restriction: Optional[Dict[str, List[str]]] = None,
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
        data = await self._http.post("/api/v1/links", json=body)
        return Link.model_validate(data)

    async def list(self, *, limit: int = 20, offset: int = 0) -> LinkList:
        data = await self._http.get("/api/v1/links", params={"limit": limit, "offset": offset})
        return LinkList.model_validate(data)

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
        routing_rules: Optional[List[Dict[str, str]]] = None,
        og_meta: Optional[Dict[str, str]] = None,
        geo_restriction: Optional[Dict[str, List[str]]] = None,
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
        data = await self._http.patch(f"/api/v1/links/{short_path}", json=body)
        return Link.model_validate(data)

    async def delete(self, short_path: str) -> None:
        await self._http.delete(f"/api/v1/links/{short_path}")
