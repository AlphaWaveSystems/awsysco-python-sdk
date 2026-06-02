"""Async Tags resource."""

from __future__ import annotations

from urllib.parse import quote

from .._async_http import AsyncHttpClient


class AsyncTagsResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def add(self, short_path: str, tag: str) -> dict:
        encoded = quote(short_path, safe="")
        return await self._http.post(f"/api/link/{encoded}/tags", json={"tag": tag}) or {}

    async def remove(self, short_path: str, tag: str) -> dict:
        encoded = quote(short_path, safe="")
        encoded_tag = quote(tag, safe="")
        return await self._http.delete(f"/api/link/{encoded}/tags/{encoded_tag}") or {}
