"""Async Analytics resource."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._async_http import AsyncHttpClient
from ..models import AggregateAnalytics, ClickEvent, LinkStats


class AsyncAnalyticsResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def get_stats(self, short_path: str, *, period: Optional[str] = None) -> LinkStats:
        params: Dict[str, Any] = {}
        if period is not None:
            params["period"] = period
        data = await self._http.get(
            f"/api/v1/links/{short_path}/stats",
            params=params if params else None,
        )
        return LinkStats.model_validate(data)

    async def get_aggregate_stats(
        self, short_path: str, *, period: Optional[str] = None
    ) -> AggregateAnalytics:
        params: Dict[str, Any] = {}
        if period is not None:
            params["period"] = period
        data = await self._http.get(
            f"/api/v1/links/{short_path}/stats/aggregate",
            params=params if params else None,
        )
        return AggregateAnalytics.model_validate(data)

    async def get_recent_clicks(
        self, *, limit: Optional[int] = None, since: Optional[str] = None
    ) -> List[ClickEvent]:
        """Requires the "Live Globe" feature flag; disabled accounts get a 403
        ``FEATURE_DISABLED`` (surfaces as ``AwsysForbiddenError``)."""
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if since is not None:
            params["since"] = since
        data = await self._http.get(
            "/api/user/clicks/recent",
            params=params if params else None,
        )
        if isinstance(data, list):
            return [ClickEvent.model_validate(item) for item in data]
        items = data.get("clicks", data.get("recentClicks", []))
        return [ClickEvent.model_validate(item) for item in items]
