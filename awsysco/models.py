"""Pydantic v2 models for AWSYS.CO API request and response types."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


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
