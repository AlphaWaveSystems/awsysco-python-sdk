"""QR code resource — URL construction for QR code images."""

from __future__ import annotations

from urllib.parse import urlencode

from .._http import HttpClient


class QRResource:
    """Build QR code image URLs for shortened links.

    No HTTP requests are made — this resource constructs the URL only.
    """

    def __init__(self, http: HttpClient) -> None:
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
