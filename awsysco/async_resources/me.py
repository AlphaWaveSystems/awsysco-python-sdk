"""Async Me resource."""

from __future__ import annotations

from .._async_http import AsyncHttpClient
from ..models import MeResponse


class AsyncMeResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def get(self) -> MeResponse:
        data = await self._http.get("/api/v1/me")
        return MeResponse.model_validate(data)
