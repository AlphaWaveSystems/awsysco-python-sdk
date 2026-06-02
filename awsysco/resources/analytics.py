"""Analytics resource — link click statistics."""

from __future__ import annotations

from typing import List, Optional

from .._http import HttpClient
from ..models import ClickEvent, LinkStats


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
        params = {}
        if period is not None:
            params["period"] = period
        data = self._http.get(
            f"/api/v1/links/{short_path}/stats",
            params=params if params else None,
        )
        return LinkStats.model_validate(data)

    def get_recent_clicks(self, *, limit: Optional[int] = None) -> List[ClickEvent]:
        """Get recent click events across all links for the authenticated user.

        Args:
            limit: Maximum number of click events to return.

        Returns:
            A list of ClickEvent objects.
        """
        params = {}
        if limit is not None:
            params["limit"] = limit
        data = self._http.get(
            "/api/user/recent-clicks",
            params=params if params else None,
        )
        if isinstance(data, list):
            return [ClickEvent.model_validate(item) for item in data]
        # Some API shapes wrap in a key
        items = data.get("clicks", data.get("recentClicks", []))
        return [ClickEvent.model_validate(item) for item in items]
