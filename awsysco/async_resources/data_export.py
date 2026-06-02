"""Async Data Export resource."""

from __future__ import annotations

from .._async_http import AsyncHttpClient


class AsyncDataExportResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def export_links(self) -> str:
        return await self._http.get_text("/api/export/links")

    async def export_link_stats(self, short_path: str) -> str:
        return await self._http.get_text(f"/api/export/stats/{short_path}")
