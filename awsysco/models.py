"""Pydantic v2 models for AWSYS.CO API request and response types."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel


def _coerce_firestore_timestamps(data: Any) -> Any:
    """Convert any top-level Firestore ``{_seconds,_nanoseconds}``/``{seconds,nanoseconds}``
    value to an ISO-8601 string, in place, before field validation runs.

    Per the cross-SDK contract, timestamp fields must accept both plain ISO-8601
    strings and Firestore's raw timestamp shape. Fields stay typed as ``Optional[str]``
    (upgrading to a native ``datetime`` would be a breaking type change for a minor
    release) — an unrecognized shape is left untouched rather than raising, since a
    parse failure here must never crash model validation.
    """
    if not isinstance(data, dict):
        return data
    result = dict(data)
    for key, value in data.items():
        if not isinstance(value, dict):
            continue
        # Only treat this as an *attempted* timestamp if a seconds-like key is
        # actually present — a dict with neither key is presumed unrelated (e.g.
        # a genuinely dict-typed field like MeResponse.features) and left alone.
        if "_seconds" not in value and "seconds" not in value:
            continue
        seconds = value.get("_seconds", value.get("seconds"))
        nanos = value.get("_nanoseconds", value.get("nanoseconds", 0))
        try:
            if not isinstance(seconds, (int, float)) or isinstance(seconds, bool):
                raise TypeError(f"non-numeric seconds: {seconds!r}")
            if not isinstance(nanos, (int, float)) or isinstance(nanos, bool):
                nanos = 0
            dt = datetime.fromtimestamp(seconds + nanos / 1e9, tz=timezone.utc)
            result[key] = dt.isoformat().replace("+00:00", "Z")
        except (OverflowError, OSError, ValueError, TypeError):
            # A shape that declared itself a Firestore timestamp (has a seconds
            # key) but doesn't actually convert (huge/negative/non-numeric
            # seconds, non-numeric nanoseconds, etc.) must still never crash
            # model validation — but leaving the raw dict in place would just
            # move the crash downstream into field validation (a dict into an
            # Optional[str] field). Stringify it instead so the field always
            # gets a string.
            result[key] = str(value)
    return result

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
    "UsageLimits",
    "UsageOverage",
    "UsageStats",
    "Web2AppSession",
    "ImportCounts",
    "ImportJob",
    "DayClicks",
    "HourClicks",
    "DeviceBreakdown",
    "UTMBreakdown",
    "UpgradeForMore",
    "AggregateAnalytics",
    "Profile",
]


class _CamelModel(BaseModel):
    """Base model that accepts camelCase field names from the API."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="allow",
    )

    @model_validator(mode="before")
    @classmethod
    def _coerce_timestamps(cls, data: Any) -> Any:
        return _coerce_firestore_timestamps(data)


# ---------------------------------------------------------------------------
# Link models
# ---------------------------------------------------------------------------


class Link(_CamelModel):
    """A shortened link returned by the API."""

    id: Optional[str] = None
    short_url: Optional[str] = None
    short_code: Optional[str] = None
    full_path: Optional[str] = None
    namespace: Optional[str] = None
    long: Optional[str] = None
    clicks: Optional[int] = None
    created: Optional[str] = None
    expires_at: Optional[str] = None
    max_clicks: Optional[int] = None
    expire_fallback_url: Optional[str] = None
    password_protected: Optional[bool] = None


class LinkList(_CamelModel):
    """Paginated list of links.

    The platform nests pagination info under a ``pagination`` object
    (``{links: [...], pagination: {limit, offset, hasMore}}``), not at the top
    level — the before-validator below hoists those fields up so ``has_more``
    (and ``limit``/``offset``) actually populate instead of always being ``None``.
    """

    links: List[Link] = Field(default_factory=list)
    total: Optional[int] = None
    has_more: Optional[bool] = None
    limit: Optional[int] = None
    offset: Optional[int] = None

    @model_validator(mode="before")
    @classmethod
    def _hoist_pagination(cls, data: Any) -> Any:
        if isinstance(data, dict) and isinstance(data.get("pagination"), dict):
            # pagination.* is the only source of truth once present — it must
            # win over any stray top-level key of the same name, not just fill
            # one in if absent.
            pagination = data["pagination"]
            data = dict(data)
            data["hasMore"] = pagination.get("hasMore")
            data["limit"] = pagination.get("limit")
            data["offset"] = pagination.get("offset")
        return data


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
    """Result of a URL trust/safety scan.

    Wire keys are ``shortCode``/``trustScore``/``trustStatus`` — ``short``/``long``
    are kept as separate (currently unpopulated) fields since the platform doesn't
    send them under those names; removing them would be a breaking change.
    """

    short: Optional[str] = None
    long: Optional[str] = None
    short_code: Optional[str] = None
    score: Optional[float] = Field(default=None, alias="trustScore")
    status: Optional[str] = Field(default=None, alias="trustStatus")
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
    """A registered webhook endpoint.

    Legacy webhook documents on the platform may omit every field but
    ``id``/``url``/``events`` (no ``enabled``, ``secret``, etc.) — all other fields
    stay ``Optional`` and default to ``None`` rather than a guessed default.
    """

    id: Optional[str] = None
    url: Optional[str] = None
    events: List[str] = Field(default_factory=list)
    name: Optional[str] = None
    # `repr=False` excludes this from BOTH __repr__ and __str__ — pydantic's default
    # __str__ is backed by the same __repr_args__ machinery as __repr__, so this is
    # enough to keep the secret out of str(webhook)/f"{webhook}"/print(webhook) too.
    secret: Optional[str] = Field(default=None, repr=False)
    enabled: Optional[bool] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_triggered: Optional[str] = None
    failure_count: Optional[int] = None
    success_count: Optional[int] = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__repr_str__(', ')})"  # type: ignore[misc]

    __str__ = __repr__


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
    default_redirect: Optional[str] = None


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


# ---------------------------------------------------------------------------
# Usage models — live consumption + tier limits
# ---------------------------------------------------------------------------


class UsageLimits(_CamelModel):
    """Tier limits as reported by ``/api/user/stats``.

    Several limit fields may be either an integer cap or the string
    ``"unlimited"`` (the API serializes an unlimited cap of ``-1`` as the
    literal ``"unlimited"``), so those are typed as ``Union[int, str]``.
    """

    links_per_month: Optional[Union[int, str]] = None
    monthly_links: Optional[Union[int, str]] = None
    daily_links: Optional[Union[int, str]] = None
    monthly_tracked_clicks: Optional[Union[int, str]] = None
    qr_codes: Optional[Union[int, str]] = None
    folders: Optional[Union[int, str]] = None
    api_calls_per_month: Optional[int] = None
    custom_slugs: Optional[int] = None


class UsageOverage(_CamelModel):
    """Overage (pay-as-you-go) state within the current billing cycle."""

    active: Optional[bool] = None
    started_at: Optional[str] = None
    expires_at: Optional[str] = None
    hours_until_drop: Optional[float] = None
    clicks_this_cycle: Optional[int] = None
    spending_limit_cents: Optional[int] = None
    estimated_charge_cents: Optional[int] = None


class UsageStats(_CamelModel):
    """Live consumption stats from ``/api/user/stats``."""

    total_links: Optional[int] = None
    total_clicks: Optional[int] = None
    links_created_this_month: Optional[int] = None
    qr_codes_this_month: Optional[int] = None
    folder_count: Optional[int] = None
    api_calls_this_month: Optional[int] = None
    tracked_clicks_this_month: Optional[int] = None
    tier: Optional[str] = None
    limits: Optional[UsageLimits] = None
    has_api_key: Optional[bool] = None
    api_key_created_at: Optional[str] = None
    user_prefix: Optional[str] = None
    is_premium: Optional[bool] = None
    overage: Optional[UsageOverage] = None


# ---------------------------------------------------------------------------
# Web2App model
# ---------------------------------------------------------------------------


class Web2AppSession(_CamelModel):
    """A single-use Web2App deep-link session returned by
    ``/api/v1/web2app/{token}``.

    Sessions are single-use (consumed on read) with a 24-hour TTL.
    """

    success: Optional[bool] = None
    link_id: Optional[str] = None
    utm_params: Dict[str, str] = Field(default_factory=dict)
    routing_rule: Optional[Dict[str, Any]] = None
    country: Optional[str] = None
    clicked_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Imports models — provider link-import jobs
# ---------------------------------------------------------------------------


class ImportCounts(_CamelModel):
    """Progress counters for an import job."""

    fetched: int = 0
    transformed: int = 0
    written: int = 0
    errored: int = 0


class ImportJob(_CamelModel):
    """A provider link-import job from ``/api/v1/imports``.

    ``status`` progresses through states such as ``pending``, ``running``,
    ``completed``, ``partial``, ``failed``, and ``cancelled``.
    """

    id: Optional[str] = None
    user_id: Optional[str] = None
    provider: Optional[str] = None
    status: Optional[str] = None
    scan_only: Optional[bool] = None
    target_namespace: Optional[str] = None
    scope_filter: Optional[str] = None
    counts: Optional[ImportCounts] = None
    errors: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Aggregate analytics models — tier-gated rollups
# ---------------------------------------------------------------------------


class DayClicks(_CamelModel):
    """Clicks for a single calendar day."""

    date: Optional[str] = None
    clicks: Optional[int] = None


class HourClicks(_CamelModel):
    """Clicks for a single hour-of-day bucket (0–23)."""

    hour: Optional[int] = None
    clicks: Optional[int] = None


class DeviceBreakdown(_CamelModel):
    """Click counts split by device class."""

    mobile: Optional[int] = None
    desktop: Optional[int] = None
    tablet: Optional[int] = None


class UTMBreakdown(_CamelModel):
    """UTM rollups keyed by source / medium / campaign."""

    sources: Dict[str, int] = Field(default_factory=dict)
    mediums: Dict[str, int] = Field(default_factory=dict)
    campaigns: Dict[str, int] = Field(default_factory=dict)


class UpgradeForMore(_CamelModel):
    """Tier-gating hint listing breakdowns available on higher tiers."""

    available: List[str] = Field(default_factory=list)
    message: Optional[str] = None


class AggregateAnalytics(_CamelModel):
    """Aggregated click analytics from
    ``/api/v1/links/{short_path}/stats/aggregate``.

    The set of populated breakdowns depends on the account tier — free-tier
    responses include ``upgrade_for_more`` and omit the richer breakdowns,
    while higher tiers populate ``device_breakdown``, ``utm_breakdown``, etc.
    """

    short_code: Optional[str] = None
    full_path: Optional[str] = None
    period: Optional[str] = None
    total_clicks: Optional[int] = None
    unique_visitors: Optional[int] = None
    clicks_by_day: List[DayClicks] = Field(default_factory=list)
    country_breakdown: Dict[str, int] = Field(default_factory=dict)
    tier_limit: Optional[int] = None
    tier: Optional[str] = None
    device_breakdown: Optional[DeviceBreakdown] = None
    referrer_breakdown: Optional[Dict[str, int]] = None
    browser_breakdown: Optional[Dict[str, int]] = None
    os_breakdown: Optional[Dict[str, int]] = None
    source_breakdown: Optional[Dict[str, int]] = None
    hour_breakdown: Optional[List[HourClicks]] = None
    utm_breakdown: Optional[UTMBreakdown] = None
    upgrade_for_more: Optional[UpgradeForMore] = None


# ---------------------------------------------------------------------------
# Profile model — /api/user/profile
# ---------------------------------------------------------------------------


class Profile(_CamelModel):
    """The authenticated user's account profile.

    Distinct from :class:`MeResponse` (subscription tier/feature summary) and
    :class:`UsageStats` (live consumption counters). Unknown fields returned by the
    platform are preserved (``extra="allow"`` on the base model).
    """

    uid: Optional[str] = None
    email: Optional[str] = None
    display_name: Optional[str] = None
    created_at: Optional[str] = None
