"""Data Export resource — CSV exports for links and link stats."""

from __future__ import annotations

from .._http import HttpClient


class DataExportResource:
    """Interact with /api/export endpoints that return CSV data."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def export_links(self) -> str:
        """Export all links for the authenticated user as a CSV string.

        Returns:
            A CSV-formatted string with all link data.
        """
        return self._http.get_text("/api/export/links")

    def export_link_stats(self, short_path: str) -> str:
        """Export click statistics for a specific link as a CSV string.

        Args:
            short_path: The short code or slug identifying the link.

        Returns:
            A CSV-formatted string with click statistics.
        """
        return self._http.get_text(f"/api/export/stats/{short_path}")
