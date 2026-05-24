"""AWSYS.CO API Client."""

from __future__ import annotations

from typing import Optional

from ._http import HttpClient
from .resources.analytics import AnalyticsResource
from .resources.bulk import BulkResource
from .resources.folders import FoldersResource
from .resources.links import LinksResource
from .resources.me import MeResource
from .resources.qr import QRResource

_DEFAULT_BASE_URL = "https://awsys.co"


class Client:
    """Top-level client for the AWSYS.CO API.

    Example::

        from awsysco import Client

        client = Client(api_key="awsys_...")

        # Create a short link
        link = client.links.create("https://example.com", custom_slug="demo")
        print(link.short_url)

    Args:
        api_key: Your AWSYS API key (starts with ``awsys_``).
        base_url: API base URL. Defaults to ``https://awsys.co``.
        timeout: HTTP request timeout in seconds (default 30).
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ) -> None:
        self._http = HttpClient(api_key=api_key, base_url=base_url, timeout=timeout)

        self.links = LinksResource(self._http)
        self.analytics = AnalyticsResource(self._http)
        self.qr = QRResource(self._http)
        self.folders = FoldersResource(self._http)
        self.bulk = BulkResource(self._http)
        self.me = MeResource(self._http)

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._http.close()

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
