"""Analytics resource — link click statistics."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._http import HttpClient
from ..models import AggregateAnalytics, ClickEvent, LinkStats


class AnalyticsResource:
    """Interact with /api/v1/links/:id/stats and analytics endpoints."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def get_stats(self, short_path: str, *, period: Optional[str] = None) -> LinkStats:
        """Get click analytics for a link.

        Args:
            short_path: The short code or slug identifying the link.
            period: Optional time period filter (e.g. ``'7d'``, ``'30d'``,
                ``'all'``).

        Returns:
            A LinkStats object with total_clicks and per-click breakdown.
        """
        params: Dict[str, Any] = {}
        if period is not None:
            params["period"] = period
        data = self._http.get(
            f"/api/v1/links/{short_path}/stats",
            params=params if params else None,
        )
        return LinkStats.model_validate(data)

    def get_aggregate_stats(
        self, short_path: str, *, period: Optional[str] = None
    ) -> AggregateAnalytics:
        """Get aggregated (rolled-up) click analytics for a link.

        Unlike :meth:`get_stats`, which returns a raw per-click list, this
        returns server-side aggregations (clicks by day, country/device/UTM
        breakdowns, unique visitors). The breakdowns present in the response
        are tier-gated — free-tier responses include an ``upgrade_for_more``
        hint and omit the richer breakdowns.

        Args:
            short_path: The short code or slug identifying the link.
            period: Optional time period filter (e.g. ``'7d'``, ``'30d'``,
                ``'all'``).

        Returns:
            An AggregateAnalytics object.
        """
        params: Dict[str, Any] = {}
        if period is not None:
            params["period"] = period
        data = self._http.get(
            f"/api/v1/links/{short_path}/stats/aggregate",
            params=params if params else None,
        )
        return AggregateAnalytics.model_validate(data)

    def get_recent_clicks(
        self, *, limit: Optional[int] = None, since: Optional[str] = None
    ) -> List[ClickEvent]:
        """Get recent click events across all links for the authenticated user.

        Requires the "Live Globe" feature flag to be enabled on the account — if it
        isn't, the platform returns 403 with ``code="FEATURE_DISABLED"``, which surfaces
        as :class:`~awsysco.exceptions.AwsysForbiddenError`.

        Args:
            limit: Maximum number of click events to return (platform max 50).
            since: Only return clicks after this ISO-8601 timestamp.

        Returns:
            A list of ClickEvent objects.
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if since is not None:
            params["since"] = since
        data = self._http.get(
            "/api/user/clicks/recent",
            params=params if params else None,
        )
        if isinstance(data, list):
            return [ClickEvent.model_validate(item) for item in data]
        # Some API shapes wrap in a key
        items = data.get("clicks", data.get("recentClicks", []))
        return [ClickEvent.model_validate(item) for item in items]
