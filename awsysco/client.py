"""AWSYS.CO API Client — sync and async."""

from __future__ import annotations

import os
import warnings
from typing import Optional

from ._async_http import AsyncHttpClient
from ._http import HttpClient
from ._transport import DEFAULT_MAX_RETRIES
from .async_resources.affiliate import AsyncAffiliateResource
from .async_resources.agentlink import AsyncAgentlinkResource
from .async_resources.analytics import AsyncAnalyticsResource
from .async_resources.bulk import AsyncBulkResource
from .async_resources.custom_domains import AsyncCustomDomainsResource
from .async_resources.data_export import AsyncDataExportResource
from .async_resources.folders import AsyncFoldersResource
from .async_resources.imports import AsyncImportsResource
from .async_resources.links import AsyncLinksResource
from .async_resources.me import AsyncMeResource
from .async_resources.namespace import AsyncNamespaceResource
from .async_resources.profile import AsyncProfileResource
from .async_resources.qr import AsyncQRResource
from .async_resources.saved_views import AsyncSavedViewsResource
from .async_resources.tags import AsyncTagsResource
from .async_resources.trust_score import AsyncTrustScoreResource
from .async_resources.usage import AsyncUsageResource
from .async_resources.utm_templates import AsyncUtmTemplatesResource
from .async_resources.web2app import AsyncWeb2AppResource
from .async_resources.webhooks import AsyncWebhooksResource
from .exceptions import AwsysConfigurationError
from .resources.affiliate import AffiliateResource
from .resources.agentlink import AgentlinkResource
from .resources.analytics import AnalyticsResource
from .resources.bulk import BulkResource
from .resources.custom_domains import CustomDomainsResource
from .resources.data_export import DataExportResource
from .resources.folders import FoldersResource
from .resources.imports import ImportsResource
from .resources.links import LinksResource
from .resources.me import MeResource
from .resources.namespace import NamespaceResource
from .resources.profile import ProfileResource
from .resources.qr import QRResource
from .resources.saved_views import SavedViewsResource
from .resources.tags import TagsResource
from .resources.trust_score import TrustScoreResource
from .resources.usage import UsageResource
from .resources.utm_templates import UtmTemplatesResource
from .resources.web2app import Web2AppResource
from .resources.webhooks import WebhooksResource

_DEFAULT_BASE_URL = "https://awsys.co"


_warned_non_awsys_key = False


def _resolve_api_key(api_key: Optional[str]) -> str:
    global _warned_non_awsys_key
    resolved = api_key if api_key is not None else os.environ.get("AWSYS_API_KEY")
    if not resolved:
        raise AwsysConfigurationError(
            "No API key provided. Pass api_key=... or set the AWSYS_API_KEY "
            "environment variable."
        )
    if not resolved.startswith("awsys_") and not _warned_non_awsys_key:
        _warned_non_awsys_key = True
        warnings.warn(
            "This does not look like an AWSYS API key (expected it to start with "
            "'awsys_').",
            stacklevel=3,
        )
    return resolved


def _resolve_base_url(base_url: Optional[str]) -> str:
    if base_url is not None:
        return base_url
    return os.environ.get("AWSYS_BASE_URL", _DEFAULT_BASE_URL)


class Client:
    """Top-level synchronous client for the AWSYS.CO API.

    Example::

        from awsysco import Client

        client = Client(api_key="awsys_...")

        # Create a short link
        link = client.links.create("https://example.com", custom_slug="demo")
        print(link.short_url)

    Args:
        api_key: Your AWSYS API key (starts with ``awsys_``). Falls back to the
            ``AWSYS_API_KEY`` environment variable; raises :class:`AwsysConfigurationError`
            if neither is set.
        base_url: API base URL. Falls back to the ``AWSYS_BASE_URL`` environment variable,
            then ``https://awsys.co``. Must start with ``http://`` or ``https://``.
        timeout: HTTP request timeout in seconds (default 30). Overridable per call via
            each resource method's underlying transport.
        max_retries: Maximum retry attempts for 429s and (for idempotent methods)
            502/503/504/transport errors. ``0`` disables retries.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        resolved_key = _resolve_api_key(api_key)
        resolved_url = _resolve_base_url(base_url)
        self._http = HttpClient(
            api_key=resolved_key,
            base_url=resolved_url,
            timeout=timeout,
            max_retries=max_retries,
        )

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

        # Parity resources
        self.usage = UsageResource(self._http)
        self.web2app = Web2AppResource(self._http)
        self.imports = ImportsResource(self._http)
        self.profile = ProfileResource(self._http)

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._http.close()

    def __repr__(self) -> str:
        return f"Client(base_url={self._http.base_url!r}, api_key={self._http.redacted_key!r})"

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
        api_key: Your AWSYS API key (starts with ``awsys_``). Falls back to the
            ``AWSYS_API_KEY`` environment variable; raises :class:`AwsysConfigurationError`
            if neither is set.
        base_url: API base URL. Falls back to the ``AWSYS_BASE_URL`` environment variable,
            then ``https://awsys.co``. Must start with ``http://`` or ``https://``.
        timeout: HTTP request timeout in seconds (default 30).
        max_retries: Maximum retry attempts for 429s and (for idempotent methods)
            502/503/504/transport errors. ``0`` disables retries.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        resolved_key = _resolve_api_key(api_key)
        resolved_url = _resolve_base_url(base_url)
        self._http = AsyncHttpClient(
            api_key=resolved_key,
            base_url=resolved_url,
            timeout=timeout,
            max_retries=max_retries,
        )

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

        # Parity resources
        self.usage = AsyncUsageResource(self._http)
        self.web2app = AsyncWeb2AppResource(self._http)
        self.imports = AsyncImportsResource(self._http)
        self.profile = AsyncProfileResource(self._http)

    async def aclose(self) -> None:
        """Close the underlying async HTTP connection pool."""
        await self._http.aclose()

    def __repr__(self) -> str:
        return f"AsyncClient(base_url={self._http.base_url!r}, api_key={self._http.redacted_key!r})"

    async def __aenter__(self) -> "AsyncClient":
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()
