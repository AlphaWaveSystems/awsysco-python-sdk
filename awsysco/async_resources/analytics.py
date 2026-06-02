"""Async Analytics resource."""

from __future__ import annotations

from typing import List, Optional

from .._async_http import AsyncHttpClient
from ..models import ClickEvent, LinkStats


class AsyncAnalyticsResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def get_stats(self, short_path: str, *, period: Optional[str] = None) -> LinkStats:
        params = {}
        if period is not None:
            params["period"] = period
        data = await self._http.get(
            f"/api/v1/links/{short_path}/stats",
            params=params if params else None,
        )
        return LinkStats.model_validate(data)

    async def get_recent_clicks(self, *, limit: Optional[int] = None) -> List[ClickEvent]:
        params = {}
        if limit is not None:
            params["limit"] = limit
        data = await self._http.get(
            "/api/user/recent-clicks",
            params=params if params else None,
        )
        if isinstance(data, list):
            return [ClickEvent.model_validate(item) for item in data]
        items = data.get("clicks", data.get("recentClicks", []))
        return [ClickEvent.model_validate(item) for item in items]
