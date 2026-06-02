"""QR code resource — URL construction and settings CRUD for QR codes."""

from __future__ import annotations

from typing import Any, Dict
from urllib.parse import urlencode

from .._http import HttpClient
from ..models import QRSettings


class QRResource:
    """Build QR code image URLs and manage QR code settings for shortened links."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http
        self._base_url = http._base_url

    def get_url(
        self,
        short_code: str,
        *,
        size: int = 300,
        color: str = "000000",
        bg_color: str = "FFFFFF",
    ) -> str:
        """Build the QR code image URL for a short code.

        No HTTP request is made — this constructs the URL only.

        Args:
            short_code: The short code/slug for the link.
            size: Image size in pixels (default 300).
            color: Foreground hex color without # (default '000000').
            bg_color: Background hex color without # (default 'FFFFFF').

        Returns:
            The fully-qualified QR code image URL as a string.
        """
        params = urlencode({"size": size, "color": color, "bgColor": bg_color})
        return f"{self._base_url}/api/qr/{short_code}?{params}"

    def get_settings(self, short_path: str) -> QRSettings:
        """Get the QR code settings for a link.

        Args:
            short_path: The short code or slug identifying the link.

        Returns:
            A QRSettings object.
        """
        data = self._http.get(f"/api/link/{short_path}/qr-settings")
        return QRSettings.model_validate(data)

    def update_settings(self, short_path: str, settings: Dict[str, Any]) -> QRSettings:
        """Update the QR code settings for a link.

        Args:
            short_path: The short code or slug identifying the link.
            settings: A dict of QR settings to apply. Valid keys include
                ``size``, ``color``, ``bg_color``, ``error_correction``,
                ``margin``, and ``logo_url``.

        Returns:
            The updated QRSettings object.
        """
        data = self._http.put(f"/api/link/{short_path}/qr-settings", json=settings)
        return QRSettings.model_validate(data)
