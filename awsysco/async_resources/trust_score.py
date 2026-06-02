"""Async Trust Score resource."""

from __future__ import annotations

from urllib.parse import quote

from .._async_http import AsyncHttpClient
from ..models import TrustScoreResult


class AsyncTrustScoreResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def scan(self, short_path: str) -> TrustScoreResult:
        encoded = quote(short_path, safe="")
        data = await self._http.get(f"/api/link-scan/{encoded}")
        return TrustScoreResult.model_validate(data)
