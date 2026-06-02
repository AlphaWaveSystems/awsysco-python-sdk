"""AWSYS.CO Python SDK — Official client library for the AWSYS.CO URL Shortener API."""

from .client import AsyncClient, Client
from .exceptions import (
    AwsysAuthError,
    AwsysConflictError,
    AwsysError,
    AwsysForbiddenError,
    AwsysNotFoundError,
    AwsysRateLimitError,
    AwsysValidationError,
)
from .models import (
    AffiliateProgram,
    BulkLinkResult,
    BulkResult,
    ClickEvent,
    CustomDomain,
    Folder,
    FolderList,
    GeoRestriction,
    Link,
    LinkList,
    LinkStats,
    MeResponse,
    NamespaceCheckResult,
    NamespaceInfo,
    OgMeta,
    QRSettings,
    RoutingRule,
    SavedView,
    SavedViewFilters,
    TrustScoreResult,
    UtmTemplate,
    Webhook,
)

__version__ = "1.0.0"
__all__ = [
    # Clients
    "Client",
    "AsyncClient",
    # Exceptions
    "AwsysError",
    "AwsysAuthError",
    "AwsysForbiddenError",
    "AwsysNotFoundError",
    "AwsysConflictError",
    "AwsysValidationError",
    "AwsysRateLimitError",
    # Core models
    "Link",
    "LinkList",
    "LinkStats",
    "ClickEvent",
    "Folder",
    "FolderList",
    "BulkResult",
    "BulkLinkResult",
    "MeResponse",
    # Links advanced models
    "RoutingRule",
    "OgMeta",
    "GeoRestriction",
    # QR
    "QRSettings",
    # Trust Score
    "TrustScoreResult",
    # Namespace
    "NamespaceInfo",
    "NamespaceCheckResult",
    # UTM Templates
    "UtmTemplate",
    # Webhooks
    "Webhook",
    # Saved Views
    "SavedViewFilters",
    "SavedView",
    # Custom Domains
    "CustomDomain",
    # Affiliate
    "AffiliateProgram",
]
