"""AWSYS.CO Python SDK — Official client library for the AWSYS.CO URL Shortener API."""

from ._version import __version__
from .client import AsyncClient, Client
from .exceptions import (
    AwsysAuthError,
    AwsysConfigurationError,
    AwsysConflictError,
    AwsysError,
    AwsysForbiddenError,
    AwsysNetworkError,
    AwsysNotFoundError,
    AwsysRateLimitError,
    AwsysServerError,
    AwsysTimeoutError,
    AwsysValidationError,
)
from .models import (
    AffiliateProgram,
    AggregateAnalytics,
    BulkLinkResult,
    BulkResult,
    ClickEvent,
    CustomDomain,
    DayClicks,
    DeviceBreakdown,
    Folder,
    FolderList,
    GeoRestriction,
    HourClicks,
    ImportCounts,
    ImportJob,
    Link,
    LinkList,
    LinkStats,
    MeResponse,
    NamespaceCheckResult,
    NamespaceInfo,
    OgMeta,
    Profile,
    QRSettings,
    RoutingRule,
    SavedView,
    SavedViewFilters,
    TrustScoreResult,
    UpgradeForMore,
    UsageLimits,
    UsageOverage,
    UsageStats,
    UTMBreakdown,
    UtmTemplate,
    Web2AppSession,
    Webhook,
)

__all__ = [
    # Version
    "__version__",
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
    "AwsysServerError",
    "AwsysNetworkError",
    "AwsysTimeoutError",
    "AwsysConfigurationError",
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
    # Usage
    "UsageStats",
    "UsageLimits",
    "UsageOverage",
    # Profile
    "Profile",
    # Web2App
    "Web2AppSession",
    # Imports
    "ImportCounts",
    "ImportJob",
    # Aggregate analytics
    "AggregateAnalytics",
    "DayClicks",
    "HourClicks",
    "DeviceBreakdown",
    "UTMBreakdown",
    "UpgradeForMore",
]
