"""Async QR resource."""

from __future__ import annotations

from typing import Any, Dict
from urllib.parse import urlencode

from .._async_http import AsyncHttpClient
from ..models import QRSettings


class AsyncQRResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http
        self._base_url = http._base_url

    def get_url(self, short_code: str, *, size: int = 300, color: str = "000000", bg_color: str = "FFFFFF") -> str:
        params = urlencode({"size": size, "color": color, "bgColor": bg_color})
        return f"{self._base_url}/api/qr/{short_code}?{params}"

    async def get_settings(self, short_path: str) -> QRSettings:
        data = await self._http.get(f"/api/link/{short_path}/qr-settings")
        return QRSettings.model_validate(data)

    async def update_settings(self, short_path: str, settings: Dict[str, Any]) -> QRSettings:
        data = await self._http.put(f"/api/link/{short_path}/qr-settings", json=settings)
        return QRSettings.model_validate(data)
