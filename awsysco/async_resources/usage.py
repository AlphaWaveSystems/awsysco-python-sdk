"""Async Usage resource."""

from __future__ import annotations

from .._async_http import AsyncHttpClient
from ..models import UsageStats


class AsyncUsageResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def get(self) -> UsageStats:
        """Get live consumption stats for the authenticated account.

        Unlike ``me.get()`` (static profile), this returns live usage
        counters, current tier limits, and any active overage state.
        """
        data = await self._http.get("/api/user/stats")
        return UsageStats.model_validate(data)
