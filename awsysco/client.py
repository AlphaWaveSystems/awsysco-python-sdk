"""AWSYS.CO API Client — sync and async."""

from __future__ import annotations

from typing import Optional

from ._async_http import AsyncHttpClient
from ._http import HttpClient
from .async_resources.affiliate import AsyncAffiliateResource
from .async_resources.agentlink import AsyncAgentlinkResource
from .async_resources.analytics import AsyncAnalyticsResource
from .async_resources.bulk import AsyncBulkResource
from .async_resources.custom_domains import AsyncCustomDomainsResource
from .async_resources.data_export import AsyncDataExportResource
from .async_resources.folders import AsyncFoldersResource
from .async_resources.links import AsyncLinksResource
from .async_resources.me import AsyncMeResource
from .async_resources.namespace import AsyncNamespaceResource
from .async_resources.qr import AsyncQRResource
from .async_resources.saved_views import AsyncSavedViewsResource
from .async_resources.tags import AsyncTagsResource
from .async_resources.trust_score import AsyncTrustScoreResource
from .async_resources.utm_templates import AsyncUtmTemplatesResource
from .async_resources.webhooks import AsyncWebhooksResource
from .resources.affiliate import AffiliateResource
from .resources.agentlink import AgentlinkResource
from .resources.analytics import AnalyticsResource
from .resources.bulk import BulkResource
from .resources.custom_domains import CustomDomainsResource
from .resources.data_export import DataExportResource
from .resources.folders import FoldersResource
from .resources.links import LinksResource
from .resources.me import MeResource
from .resources.namespace import NamespaceResource
from .resources.qr import QRResource
from .resources.saved_views import SavedViewsResource
from .resources.tags import TagsResource
from .resources.trust_score import TrustScoreResource
from .resources.utm_templates import UtmTemplatesResource
from .resources.webhooks import WebhooksResource

_DEFAULT_BASE_URL = "https://awsys.co"


class Client:
    """Top-level synchronous client for the AWSYS.CO API.

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

        # Core resources
        self.links = LinksResource(self._http)
        self.analytics = AnalyticsResource(self._http)
        self.qr = QRResource(self._http)
        self.folders = FoldersResource(self._http)
        self.bulk = BulkResource(self._http)
        self.me = MeResource(self._http)

        # Phase 2 — simple new resources
        self.tags = TagsResource(self._http)
        self.trust_score = TrustScoreResource(self._http)
        self.data_export = DataExportResource(self._http)
        self.namespace = NamespaceResource(self._http)
        self.utm_templates = UtmTemplatesResource(self._http)

        # Phase 3 — complex new resources
        self.webhooks = WebhooksResource(self._http)
        self.saved_views = SavedViewsResource(self._http)
        self.custom_domains = CustomDomainsResource(self._http)
        self.agentlink = AgentlinkResource(self._http)
        self.affiliate = AffiliateResource(self._http)

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._http.close()

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class AsyncClient:
    """Top-level asynchronous client for the AWSYS.CO API.

    Use as an async context manager::

        from awsysco import AsyncClient

        async with AsyncClient(api_key="awsys_...") as client:
            link = await client.links.create("https://example.com")
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
        self._http = AsyncHttpClient(api_key=api_key, base_url=base_url, timeout=timeout)

        # Core resources
        self.links = AsyncLinksResource(self._http)
        self.analytics = AsyncAnalyticsResource(self._http)
        self.qr = AsyncQRResource(self._http)
        self.folders = AsyncFoldersResource(self._http)
        self.bulk = AsyncBulkResource(self._http)
        self.me = AsyncMeResource(self._http)

        # Phase 2 — simple new resources
        self.tags = AsyncTagsResource(self._http)
        self.trust_score = AsyncTrustScoreResource(self._http)
        self.data_export = AsyncDataExportResource(self._http)
        self.namespace = AsyncNamespaceResource(self._http)
        self.utm_templates = AsyncUtmTemplatesResource(self._http)

        # Phase 3 — complex new resources
        self.webhooks = AsyncWebhooksResource(self._http)
        self.saved_views = AsyncSavedViewsResource(self._http)
        self.custom_domains = AsyncCustomDomainsResource(self._http)
        self.agentlink = AsyncAgentlinkResource(self._http)
        self.affiliate = AsyncAffiliateResource(self._http)

    async def aclose(self) -> None:
        """Close the underlying async HTTP connection pool."""
        await self._http.aclose()

    async def __aenter__(self) -> "AsyncClient":
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()
