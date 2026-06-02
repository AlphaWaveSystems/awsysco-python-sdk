"""Async Namespace resource."""

from __future__ import annotations

from .._async_http import AsyncHttpClient
from ..models import NamespaceCheckResult, NamespaceInfo


class AsyncNamespaceResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def get(self) -> NamespaceInfo:
        data = await self._http.get("/api/user/namespace")
        return NamespaceInfo.model_validate(data)

    async def check(self, namespace: str) -> NamespaceCheckResult:
        data = await self._http.get(f"/api/namespace/check/{namespace}")
        return NamespaceCheckResult.model_validate(data)

    async def claim(self, namespace: str) -> NamespaceInfo:
        data = await self._http.post("/api/user/namespace", json={"namespace": namespace})
        return NamespaceInfo.model_validate(data)

    async def release(self) -> dict:
        return await self._http.delete("/api/user/namespace") or {}
