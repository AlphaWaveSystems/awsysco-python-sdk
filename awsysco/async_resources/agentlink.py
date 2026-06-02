"""Async AgentLink resource."""

from __future__ import annotations

from .._async_http import AsyncHttpClient


class AsyncAgentlinkResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def subscribe(self, email: str) -> dict:
        return await self._http.post("/api/agentlink/subscribe", json={"email": email}) or {}

    async def get_link_stats(self, short_path: str, *, period_days: int = 7) -> dict:
        return await self._http.get(f"/api/agentlink/links/{short_path}/stats", params={"period": period_days}) or {}

    async def get_account_stats(self, *, period_days: int = 7) -> dict:
        return await self._http.get("/api/agentlink/account/stats", params={"period": period_days}) or {}
