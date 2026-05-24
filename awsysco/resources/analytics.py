"""Analytics resource — link click statistics."""

from __future__ import annotations

from .._http import HttpClient
from ..models import LinkStats


class AnalyticsResource:
    """Interact with /api/v1/links/:id/stats."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def get_stats(self, short_path: str) -> LinkStats:
        """Get click analytics for a link.

        Args:
            short_path: The short code or slug identifying the link.

        Returns:
            A LinkStats object with total_clicks and per-click breakdown.
        """
        data = self._http.get(f"/api/v1/links/{short_path}/stats")
        return LinkStats.model_validate(data)
