"""Pydantic v2 models for AWSYS.CO API request and response types."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

__all__ = [
    "Link",
    "LinkList",
    "LinkStats",
    "ClickEvent",
    "Folder",
    "FolderList",
    "BulkResult",
    "BulkLinkResult",
    "MeResponse",
    "RoutingRule",
    "OgMeta",
    "GeoRestriction",
    "QRSettings",
    "TrustScoreResult",
    "NamespaceInfo",
    "NamespaceCheckResult",
    "UtmTemplate",
    "Webhook",
    "SavedViewFilters",
    "SavedView",
    "CustomDomain",
    "AffiliateProgram",
]


class _CamelModel(BaseModel):
    """Base model that accepts camelCase field names from the API."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="allow",
    )


# ---------------------------------------------------------------------------
# Link models
# ---------------------------------------------------------------------------


class Link(_CamelModel):
    """A shortened link returned by the API."""

    id: Optional[str] = None
    short_url: Optional[str] = None
    short_code: Optional[str] = None
    long: Optional[str] = None
    clicks: Optional[int] = None
    created: Optional[str] = None
    expires_at: Optional[str] = None
    max_clicks: Optional[int] = None
    expire_fallback_url: Optional[str] = None
    password_protected: Optional[bool] = None


class LinkList(_CamelModel):
    """Paginated list of links."""

    links: List[Link] = Field(default_factory=list)
    total: Optional[int] = None
    has_more: Optional[bool] = None


# ---------------------------------------------------------------------------
# Analytics models
# ---------------------------------------------------------------------------


class ClickEvent(_CamelModel):
    """A single click event in link analytics."""

    timestamp: Optional[str] = None
    country: Optional[str] = None
    device: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    referrer: Optional[str] = None


class LinkStats(_CamelModel):
    """Analytics stats for a link."""

    short_code: Optional[str] = None
    total_clicks: Optional[int] = None
    clicks: List[ClickEvent] = Field(default_factory=list)
    aggregate_stats: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# Folder models
# ---------------------------------------------------------------------------


class Folder(_CamelModel):
    """A link folder."""

    id: Optional[str] = None
    name: Optional[str] = None
    color: Optional[str] = None
    link_count: Optional[int] = None
    created_at: Optional[str] = None


class FolderList(_CamelModel):
    """Response from listing folders."""

    folders: List[Folder] = Field(default_factory=list)
    limit: Optional[int] = None
    used: Optional[int] = None


# ---------------------------------------------------------------------------
# Bulk models
# ---------------------------------------------------------------------------


class BulkLinkResult(_CamelModel):
    """Result for a single URL in a bulk create operation."""

    success: Optional[bool] = None
    short_url: Optional[str] = None
    long: Optional[str] = None
    error: Optional[str] = None


class BulkResult(_CamelModel):
    """Response from a bulk link create operation."""

    created: Optional[int] = None
    failed: Optional[int] = None
    results: List[BulkLinkResult] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Me model
# ---------------------------------------------------------------------------


class MeResponse(_CamelModel):
    """Response from /api/v1/me."""

    uid: Optional[str] = None
    email: Optional[str] = None
    subscription_tier: Optional[str] = None
    user_prefix: Optional[str] = None
    is_premium: Optional[bool] = None
    features: Optional[Dict[str, Any]] = None
    limits: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# Links — advanced field models
# ---------------------------------------------------------------------------


class RoutingRule(_CamelModel):
    """A geo-routing rule for a link."""

    country: Optional[str] = None
    redirect_url: Optional[str] = None


class OgMeta(_CamelModel):
    """Open Graph metadata override for a link."""

    title: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None


class GeoRestriction(_CamelModel):
    """Geo-restriction settings for a link."""

    allowed_countries: Optional[List[str]] = None
    blocked_countries: Optional[List[str]] = None


# ---------------------------------------------------------------------------
# QR Settings model
# ---------------------------------------------------------------------------


class QRSettings(_CamelModel):
    """QR code settings for a link."""

    size: Optional[int] = None
    color: Optional[str] = None
    bg_color: Optional[str] = None
    error_correction: Optional[str] = None
    margin: Optional[int] = None
    logo_url: Optional[str] = None


# ---------------------------------------------------------------------------
# Trust Score model
# ---------------------------------------------------------------------------


class TrustScoreResult(_CamelModel):
    """Result of a URL trust/safety scan."""

    short: Optional[str] = None
    long: Optional[str] = None
    score: Optional[float] = None
    status: Optional[str] = None
    threats: Optional[List[str]] = None
    scanned_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Namespace models
# ---------------------------------------------------------------------------


class NamespaceInfo(_CamelModel):
    """Namespace info for the authenticated user."""

    has_access: Optional[bool] = None
    namespace: Optional[str] = None
    tier: Optional[str] = None
    upgrade_required: Optional[bool] = None


class NamespaceCheckResult(_CamelModel):
    """Result of checking namespace availability."""

    namespace: Optional[str] = None
    available: Optional[bool] = None
    reason: Optional[str] = None
    preview_url: Optional[str] = None


# ---------------------------------------------------------------------------
# UTM Template model
# ---------------------------------------------------------------------------


class UtmTemplate(_CamelModel):
    """A saved UTM parameter template."""

    id: Optional[str] = None
    name: Optional[str] = None
    source: Optional[str] = None
    medium: Optional[str] = None
    campaign: Optional[str] = None
    term: Optional[str] = None
    content: Optional[str] = None


# ---------------------------------------------------------------------------
# Webhook model
# ---------------------------------------------------------------------------


class Webhook(_CamelModel):
    """A registered webhook endpoint."""

    id: Optional[str] = None
    url: Optional[str] = None
    events: List[str] = Field(default_factory=list)
    name: Optional[str] = None
    enabled: Optional[bool] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_triggered: Optional[str] = None
    failure_count: Optional[int] = None


# ---------------------------------------------------------------------------
# Saved View models
# ---------------------------------------------------------------------------


class SavedViewFilters(_CamelModel):
    """Filter criteria for a saved view."""

    folder_id: Optional[str] = None
    tag: Optional[str] = None
    status: Optional[str] = None
    search: Optional[str] = None
    date_range: Optional[str] = None


class SavedView(_CamelModel):
    """A saved dashboard view with filter presets."""

    id: Optional[str] = None
    name: Optional[str] = None
    filters: Optional[SavedViewFilters] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Custom Domain model
# ---------------------------------------------------------------------------


class CustomDomain(_CamelModel):
    """A custom domain registered to the user's account."""

    domain: Optional[str] = None
    status: Optional[str] = None
    verification_token: Optional[str] = None
    is_default: Optional[bool] = None
    link_count: Optional[int] = None
    created_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Affiliate Program model
# ---------------------------------------------------------------------------


class AffiliateProgram(_CamelModel):
    """An affiliate program."""

    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    commission_type: Optional[str] = None
    cpc_rate: Optional[float] = None
    cpa_rate: Optional[float] = None
    cookie_days: Optional[int] = None
    status: Optional[str] = None
