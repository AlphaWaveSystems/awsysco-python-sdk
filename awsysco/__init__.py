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

__version__ = "1.3.0"
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
    # Usage
    "UsageStats",
    "UsageLimits",
    "UsageOverage",
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
